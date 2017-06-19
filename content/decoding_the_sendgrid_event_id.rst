Decoding the SendGrid event ID
##############################

:date: 2017-06-11 21:30
:tags: sendgrid, uuid, base64
:category: tech
:authors: Emiel van de Laar

SendGrid_ is a managed email delivery service. A webhook_ is offered which can
notify you when interesting events happen while processing your email. The
webhook will POST JSON encoded events to a URL of your choice. Each event
includes an unique identifier and is the topic of this post.

.. _SendGrid: https://sendgrid.com
.. _webhook: https://sendgrid.com/docs/API_Reference/Webhooks/event.html

Note: The following are purely my observations and corrections are welcome.

Let's have a look at a sample JSON event, particularly the *sg_event_id*
property.

.. code-block:: javascript

   {
     "email": "foo@example.com",
     "event": "processed",
     "sg_event_id": "aM7rXgTYTN-GCHRFrdsP_g",
     "sg_message_id": "<snip>",
     "smtp-id": "<snip>",
     "timestamp": 1492680648
   }

In our environment we have observed that the *sg_event_id* comes in two
different flavours (lengths). One that is *22 characaters long* and a second
that is *48 characters long*. For example:

- ``aM7rXgTYTN-GCHRFrdsP_g``
- ``ZjVhYzRhMWQtNzAzZi00ODdlLWE0YWEtYTZhNThhYWQ4OTVk``

Quick UUID Intro
----------------

While investigating the *sg_event_id* I was tipped that these were actually
UUIDs. A UUID_ is 128 bits (16 octets) long and usually presented as text. If
you're not familiar with UUIDs its best to go give the Wikipedia page a quick
glance before continuing.

.. _UUID: https://en.wikipedia.org/wiki/Universally_unique_identifier

22 character Event ID
---------------------

Let's tackle the 22 character format first by poking at it in the Python shell.

.. code-block:: python

   >>> buf = 'aM7rXgTYTN-GCHRFrdsP_g'

The string looks like it might be Base64_ encoded due to the characters
(alphabet) used (A-Z, a-z, 0-9). There are a number of Base64 encoding
alternatives that treat index values 62 and 63 differently and we need to make
sure we're using the right one. I went through our collection of event ids and
was able to identify many having both a **minus** and an **underscore**
character. And so the Base64url_ variant looks like a good candidate.

Let's pull in the ``base64`` library and attempt to decode it.

.. _Base64: https://en.wikipedia.org/wiki/Base64
.. _Base64url: https://tools.ietf.org/html/rfc4648#section-5

.. code-block:: python

   >>> import base64
   >>> base64.urlsafe_b64decode(buf)
   [snip]
   TypeError: Incorrect padding

Python gives us an ``Incorrect padding`` error. We'll skip a thorough break
down of Base64 padding but of interest is the fact that in some circumstances
padding_ is not required. If one knows the size of the data that has been
encoded the padding may be left off.

.. _padding: https://tools.ietf.org/html/rfc4648#section-3.2

.. code-block:: python

   >>> len(buf) % 4
   2

So according to the spec we need to add two padding characters, i.e. "==". We
append the padding to our *sg_event_id* and see if we can now decode it
properly.

.. code-block:: python

   >>> base64.urlsafe_b64decode(buf + '==')
   'h\xce\xeb^\x04\xd8L\xdf\x86\x08tE\xad\xdb\x0f\xfe'

Bingo, we have some bytes! 16 to be exact (you may check using len()). Let's
also encode as hex to make it a bit more readable.

.. code-block:: python

   >>> 'h\xce\xeb^\x04\xd8L\xdf\x86\x08tE\xad\xdb\x0f\xfe'.encode('hex')
   '68ceeb5e04d84cdf86087445addb0ffe'

From our intro we know that a UUID is text format representing 16 bytes. Let's
see if we can plug these bytes in and get a sensible UUID out.

.. code-block:: python

   >>> import uuid
   >>> eid = uuid.UUID(bytes='h\xce\xeb^\x04\xd8L\xdf\x86\x08tE\xad\xdb\x0f\xfe')
   >>> eid
   UUID('68ceeb5e-04d8-4cdf-8608-7445addb0ffe')
   >>> assert eid.variant == uuid.RFC_4122 and eid.version == 4

That appears to check out.

48 Character Event ID
---------------------

Now lets have a look at the *sg_event_id* having 48 characters.

.. code-block:: python

   >>> buf = "ZjVhYzRhMWQtNzAzZi00ODdlLWE0YWEtYTZhNThhYWQ4OTVk"

Again this looks like it is Base64 encoded or some variant thereof. Lets just
give it a shot.

.. code-block:: python

   >>> base64.b64decode(buf)
   'f5ac4a1d-703f-487e-a4aa-a6a58aad895d'

Hey that looks familiar. It appears to be UUIDv4 encoded string. Let's build a
UUID from the base64 decoded string and see if it checks out.

.. code-block:: python

   >>> eid = uuid.UUID('f5ac4a1d-703f-487e-a4aa-a6a58aad895d')
   >>> eid
   UUID('f5ac4a1d-703f-487e-a4aa-a6a58aad895d')
   >>> assert eid.variant == uuid.RFC_4122 and eid.version == 4

That checks out as well.

    I was unable to determine if which variant of Base64 used for this format.
    We've yet to see any special characters outside of a-z, A-Z, 0-9 alphabet.

Wrapping Up
-----------

I've applied the above decoding to all the events we've collected so far and
every id looks to be a valid UUIDv4 and so I'm fairly confident this is a valid
decoding of the *sg_event_id*.

I initially asked SendGrid support if they could point me to some documentation
or clarify the difference in the format. I didn't get a clear answer but did
mention these were generated by different systems.

Why the SendGrid UUIDs are Base64 encoded is a bit puzzling to me. A UUID
string is already URL safe because it consists of only the characters 0-9, a-f
and "-". The short format (22 chars) does take you from 32 chars (UUID string)
to 22 chars because the underlying 128 bit number is encoded. However, Base64
encoding a UUID string is going in the wrong direction as it takes you from 32
chars (UUID string) to 48.

    A final warning: SendGrid offers testing functionality to emit example
    events. The *sg_event_id* in these events has *24 characters* and is the 22
    character variant with the padding included.

Title: Decoding the SendGrid Event ID
Date: 2017-06-11 21:30
Tags: sendgrid, uuid, base64
Category: tech
Status: published
Author: Emiel van de Laar

[SendGrid](https://sendgrid.com) is a managed email delivery service. The service is able to emit notifications when something interesting happens while processing your email. When enabled, the [webhook](https://sendgrid.com/docs/API_Reference/Webhooks/event.html) will POST a collection of JSON encoded events to a URL of your choice. Each event includes a unique identifier and is the topic of this post.

> **Note:** The following are purely my observations and corrections are welcome.

Let's have a look at an example JSON event, particularly the **sg_event_id** property.

```javascript
{
"email": "foo@example.com",
"event": "processed",
"sg_event_id": "aM7rXgTYTN-GCHRFrdsP_g",
"sg_message_id": "<snip>",
"smtp-id": "<snip>",
"timestamp": 1492680648
}
```

In our environment we have observed that the _sg_event_id_ comes in two different flavors (lengths). One that is _22 characters long_ and a second that is _48 characters long_. For example:

- `aM7rXgTYTN-GCHRFrdsP_g`
- `ZjVhYzRhMWQtNzAzZi00ODdlLWE0YWEtYTZhNThhYWQ4OTVk`

## Quick UUID Intro

While investigating the _sg_event_id_ I was tipped that these were actually UUIDs. A [UUID](https://en.wikipedia.org/wiki/Universally_unique_identifier) is 128 bit number (16 octets) that is usually presented as text, e.g. _f5ac4a1d-703f-487e-a4aa-a6a58aad895d_. If you're not familiar with UUIDs I encourage you to give the Wikipedia page a quick glance before continuing.

## 22 Character Event ID

Let's tackle the 22 character format first by poking at it in the Python shell.

```python
>>> buf = 'aM7rXgTYTN-GCHRFrdsP_g'
```

The string looks like it might be [Base64](https://en.wikipedia.org/wiki/Base64) encoded due to the characters (alphabet) used (A-Z, a-z, 0-9). There are a number of Base64 encoding alternatives that treat index values 62 and 63 differently and we need to make sure we're using the right one. I went through our collection of event IDs and was able to identify many having both a **minus** and an **underscore** character. This indicates the [Base64url](https://tools.ietf.org/html/rfc4648#section-5) variant is good candidate.

Let's pull in the `base64` library and attempt to decode the event ID.

```python
>>> import base64
>>> base64.urlsafe_b64decode(buf)
[snip]
TypeError: Incorrect padding
```

Python gives us an `Incorrect padding` error. We'll skip a thorough break down of Base64 [padding](https://en.wikipedia.org/wiki/Base64#Output_padding) but of interest is the fact that some implementations discard the padding in the output because the number of missing bytes can be determined by the number of Base64 characters. In addition [RFC4648 § 5](https://tools.ietf.org/html/rfc4648#section-5)_ gives us a hint as to why one might do that.

> The pad character "=" is typically percent-encoded when used in an URI [9], but if the data length is known implicitly, this can be avoided by skipping the padding; ...

Let's see if we can figure out how much padding might have been discarded.

```python
>>> len(buf) % 4
2
# '[aM7r][XgTY][TN-G][CHRF][rdsP][_g  ]'
#         discarded padding --------^^
```

So according to the spec we need to append two padding characters, i.e. "==", to our our _sg_event_id_. Will it now decode properly?

```python
>>> base64.urlsafe_b64decode(buf + '==')
'h\xce\xeb^\x04\xd8L\xdf\x86\x08tE\xad\xdb\x0f\xfe'
```

Bingo, we have some bytes! Sixteen to be exact (you may check using len()). Let's also encode as hex to make it a bit more readable.

```python
>>> 'h\xce\xeb^\x04\xd8L\xdf\x86\x08tE\xad\xdb\x0f\xfe'.encode('hex')
'68ceeb5e04d84cdf86087445addb0ffe'
```

From our intro we know that a UUID is text format representing 16 bytes. Let's see if we can plug these bytes in and get a sensible UUID out.

```python
>>> import uuid
>>> eid = uuid.UUID(bytes='h\xce\xeb^\x04\xd8L\xdf\x86\x08tE\xad\xdb\x0f\xfe')
>>> eid
UUID('68ceeb5e-04d8-4cdf-8608-7445addb0ffe')
>>> assert eid.variant == uuid.RFC_4122 and eid.version == 4
```

That appears to check out.

## 48 Character Event ID

Now let's have a look at the _sg_event_id_ having 48 characters.

```python
>>> buf = "ZjVhYzRhMWQtNzAzZi00ODdlLWE0YWEtYTZhNThhYWQ4OTVk"
```

Again this looks like it is Base64 encoded or some variant thereof. Lets just give it a shot.

```python
>>> base64.b64decode(buf)
'f5ac4a1d-703f-487e-a4aa-a6a58aad895d'
```

Hey that looks familiar. It appears to be a UUIDv4 encoded string. Let's build a UUID from the Base64 decoded string and see if it checks out.

> **Note:** I was unable to determine which variant of Base64 is used for this format. We've yet to see any special characters outside of A-Z, a-z, 0-9 alphabet.

```python
>>> eid = uuid.UUID('f5ac4a1d-703f-487e-a4aa-a6a58aad895d')
>>> eid
UUID('f5ac4a1d-703f-487e-a4aa-a6a58aad895d')
>>> assert eid.variant == uuid.RFC_4122 and eid.version == 4
```

That appears to check out as well.

## Wrapping Up

I've applied the above decoding to all the events we've collected so far and every event id looks to be a valid UUIDv4 thus I'm fairly confident this is a valid decoding. I initially asked SendGrid support if they could point me to some documentation or clarify the difference in the format. I didn't get a clear answer but did mention these were generated by different systems.

Why the SendGrid UUIDs are Base64 encoded is a bit puzzling to me. A UUID string is already URL safe because it consists of only the characters 0-9, a-f and "-". The short format (22 chars) does take you from 32 chars (UUID string) to 22 chars because the underlying 128 bit number is encoded. However, Base64 encoding a UUID string is going in the wrong direction as it takes you from 32 chars (UUID string) to 48.

This exercise has resulted in a [Python implementation][python-impl] and a [Postgres implementation][postgres-impl]. Feel free to use them.

[python-impl]: https://gist.github.com/emiel/99e5c103dfffaf05629ca305ff546c18
[postgres-impl]: https://gist.github.com/emiel/49aa93baab83a55f17dca4f7d790a067

A final warning: SendGrid offers testing functionality to emit example events. The _sg_event_id_ in these events has _24 characters_ and is the 22 character variant with the padding included.

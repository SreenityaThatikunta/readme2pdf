# Pulsar API

A lightweight REST API for real-time pub/sub messaging.
Self-hostable, zero vendor lock-in, WebSocket support included.

---

## Base URL

```
https://api.pulsar.example.com/v1
```

All requests must include:

```
Content-Type: application/json
Authorization: Bearer <your_api_key>
```

---

## Endpoints

### Topics

| Method | Endpoint               | Description              |
|--------|------------------------|--------------------------|
| GET    | `/topics`              | List all topics          |
| POST   | `/topics`              | Create a topic           |
| DELETE | `/topics/:id`          | Delete a topic           |
| GET    | `/topics/:id/messages` | Fetch recent messages    |

### Subscriptions

| Method | Endpoint                      | Description               |
|--------|-------------------------------|---------------------------|
| GET    | `/subscriptions`              | List subscriptions        |
| POST   | `/subscriptions`              | Create a subscription     |
| DELETE | `/subscriptions/:id`          | Cancel a subscription     |

---

## Create a Topic

**POST** `/topics`

**Request body:**

```json
{
  "name": "order-events",
  "retention_hours": 48,
  "max_message_size_kb": 256
}
```

**Response:**

```json
{
  "id": "top_a8f3k2",
  "name": "order-events",
  "created_at": "2024-11-01T10:22:00Z",
  "retention_hours": 48,
  "max_message_size_kb": 256
}
```

---

## Publish a Message

**POST** `/topics/:id/publish`

```json
{
  "payload": {
    "order_id": "ord_991",
    "status": "shipped",
    "timestamp": "2024-11-01T10:30:00Z"
  },
  "key": "order-991"
}
```

---

## Client Examples

### Python

```python
import httpx

client = httpx.Client(
    base_url="https://api.pulsar.example.com/v1",
    headers={"Authorization": "Bearer sk_live_xxxx"},
)

# Publish
client.post("/topics/top_a8f3k2/publish", json={
    "payload": {"event": "user.signup", "user_id": 42},
    "key": "user-42",
})

# Fetch recent messages
resp = client.get("/topics/top_a8f3k2/messages", params={"limit": 10})
messages = resp.json()["messages"]
```

### JavaScript

```javascript
const res = await fetch("https://api.pulsar.example.com/v1/topics/top_a8f3k2/publish", {
  method: "POST",
  headers: {
    "Authorization": "Bearer sk_live_xxxx",
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    payload: { event: "page.view", path: "/home" },
    key: "session-123",
  }),
});

const data = await res.json();
console.log(data.message_id);
```

### Go

```go
package main

import (
    "bytes"
    "encoding/json"
    "fmt"
    "net/http"
)

func publish(topicID string, payload any) error {
    body, _ := json.Marshal(map[string]any{"payload": payload})
    req, _ := http.NewRequest("POST",
        fmt.Sprintf("https://api.pulsar.example.com/v1/topics/%s/publish", topicID),
        bytes.NewReader(body),
    )
    req.Header.Set("Authorization", "Bearer sk_live_xxxx")
    req.Header.Set("Content-Type", "application/json")
    _, err := http.DefaultClient.Do(req)
    return err
}
```

---

## WebSocket Streaming

Connect to receive messages in real time:

```
wss://api.pulsar.example.com/v1/topics/:id/stream?token=<api_key>
```

```javascript
const ws = new WebSocket(
  "wss://api.pulsar.example.com/v1/topics/top_a8f3k2/stream?token=sk_live_xxxx"
);

ws.onmessage = (event) => {
  const msg = JSON.parse(event.data);
  console.log("received:", msg.payload);
};
```

---

## Error Codes

| Code | Meaning                          |
|------|----------------------------------|
| 400  | Bad request / malformed JSON     |
| 401  | Invalid or missing API key       |
| 403  | Insufficient permissions         |
| 404  | Topic or resource not found      |
| 413  | Payload exceeds max size         |
| 429  | Rate limit exceeded              |
| 500  | Internal server error            |

---

## Rate Limits

| Plan     | Requests/min | Messages/day |
|----------|-------------|--------------|
| Free     | 60          | 10,000       |
| Pro      | 600         | 1,000,000    |
| Business | 6,000       | Unlimited    |

---

## Self Hosting

```bash
docker run -d \
  -p 8080:8080 \
  -e SECRET_KEY=your_secret \
  -e DATABASE_URL=postgres://... \
  ghcr.io/example/pulsar:latest
```

---

## License

Apache 2.0

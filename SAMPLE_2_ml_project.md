# NanoGrad 🧠

A minimal autograd engine and neural network library in pure Python, inspired by micrograd.
Built for learning — every line is readable, every concept is explicit.

---

## Features

- Scalar-valued autograd with reverse-mode autodiff
- Supports `+`, `-`, `*`, `/`, `**`, `relu`, `tanh`, `sigmoid`, `log`
- Multi-layer perceptron (MLP) builder
- Zero dependencies (pure Python 3.10+)

---

## Quickstart

```python
from nanograd import Value

x = Value(2.0)
y = Value(3.0)

z = x * y + y ** 2
z.backward()

print(x.grad)  # dz/dx = y = 3.0
print(y.grad)  # dz/dy = x + 2y = 2 + 6 = 8.0
```

### Training a simple MLP

```python
from nanograd import MLP

# 2 inputs → hidden layers of 4, 4 → 1 output
model = MLP(2, [4, 4, 1])

xs = [[2.0, 3.0], [-1.0, 1.0], [0.5, -0.5], [1.0, 1.0]]
ys = [1.0, -1.0, -1.0, 1.0]

for step in range(100):
    # Forward pass
    preds = [model(x)[0] for x in xs]
    loss = sum((p - y) ** 2 for p, y in zip(preds, ys))

    # Backward pass
    model.zero_grad()
    loss.backward()

    # SGD update
    for p in model.parameters():
        p.data -= 0.01 * p.grad

    if step % 10 == 0:
        print(f"step {step:3d}  loss={loss.data:.4f}")
```

---

## Core Implementation

### The `Value` class

```python
class Value:
    def __init__(self, data, _children=(), _op=""):
        self.data = float(data)
        self.grad = 0.0
        self._backward = lambda: None
        self._prev = set(_children)
        self._op = _op

    def __mul__(self, other):
        other = other if isinstance(other, Value) else Value(other)
        out = Value(self.data * other.data, (self, other), "*")

        def _backward():
            self.grad  += other.data * out.grad
            other.grad += self.data  * out.grad
        out._backward = _backward
        return out

    def tanh(self):
        t = math.tanh(self.data)
        out = Value(t, (self,), "tanh")

        def _backward():
            self.grad += (1 - t ** 2) * out.grad
        out._backward = _backward
        return out

    def backward(self):
        topo, visited = [], set()
        def build(v):
            if v not in visited:
                visited.add(v)
                for child in v._prev:
                    build(child)
                topo.append(v)
        build(self)
        self.grad = 1.0
        for node in reversed(topo):
            node._backward()
```

---

## Architecture

```
Value (scalar)
  └── __add__, __mul__, tanh, relu, ...
        └── each op records _backward closure

Neuron
  └── weights: List[Value]
  └── bias: Value
  └── forward: dot(w, x) + b → activation

Layer
  └── neurons: List[Neuron]

MLP
  └── layers: List[Layer]
  └── forward: chain layers sequentially
```

---

## Supported Operations

| Operation   | Forward               | Backward (gradient)              |
|-------------|-----------------------|----------------------------------|
| `a + b`     | `a.data + b.data`     | `grad_a += out.grad`             |
| `a * b`     | `a.data * b.data`     | `grad_a += b.data * out.grad`    |
| `a ** n`    | `a.data ** n`         | `grad_a += n * a^(n-1) * out.grad` |
| `relu(a)`   | `max(0, a.data)`      | `grad_a += out.grad if a > 0`    |
| `tanh(a)`   | `tanh(a.data)`        | `grad_a += (1 - t²) * out.grad`  |
| `log(a)`    | `log(a.data)`         | `grad_a += out.grad / a.data`    |

---

## Limitations

- Scalar only — no tensor/matrix operations
- CPU only
- Not optimised for speed — readability is the goal

For production use, see [PyTorch](https://pytorch.org) or [JAX](https://github.com/google/jax).

---

## License

MIT

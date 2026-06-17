
# 🧭 Endpoints

---

## 🟢 GET `/`

### Descripción
Endpoint de estado y bienvenida de la API.

### Respuesta

```json
{
  "message": "Bienvenid@ a Prácticas UC",
  "status": "ok",
  "service": "API de ofertas de prácticas"
}
````

---

## 🔎 GET `/ofertas`

### Descripción

Obtiene todas las ofertas de prácticas con filtros opcionales.

---

### 🔧 Query Params

| Parámetro | Tipo   | Descripción                  |
| --------- | ------ | ---------------------------- |
| area      | string | Filtra por área              |
| modalidad | string | Remota, híbrida o presencial |
| ubicacion | string | Filtra por ubicación         |
| nivel     | string | Nivel de práctica            |
| empresa   | string | Filtra por empresa           |
| activa    | 0/1    | Filtra ofertas activas       |

---

### 📌 Ejemplos

```http
GET /ofertas
GET /ofertas?area=Data
GET /ofertas?area=Ingeniería&modalidad=Remota
GET /ofertas?activa=1
```

---

### 📤 Respuesta

```json
[
  {
    "id": "uuid",
    "activa": true,
    "titulo": "Práctica Data Science",
    "empresa": "TechCorp",
    "descripcion": "Opcional",
    "ubicacion": "Santiago",
    "modalidad": "Remota",
    "area": "Data",
    "nivel": "Practica",
    "fecha_publicacion": "2026-06-15",
    "fecha_expiracion": "2026-07-15",
    "link": "https://...",
    "salario": "600000",
    "duracion": "3 meses"
  }
]
```

---

## ➕ POST `/ofertas`

### Descripción

Crea una nueva oferta de práctica.

---

### 📥 Body (JSON)

#### Obligatorios:

* titulo
* empresa
* link

#### Opcionales:

* descripcion
* ubicacion
* modalidad
* area
* nivel
* fecha_publicacion
* fecha_expiracion
* salario
* duracion

---

### 📌 Ejemplo

```json
{
  "titulo": "Práctica Backend Python",
  "empresa": "SoftSolutions",
  "link": "https://ejemplo.com",
  "descripcion": "Desarrollo de APIs con Flask",
  "ubicacion": "Santiago",
  "modalidad": "Híbrida",
  "area": "Ingeniería",
  "nivel": "Practica",
  "fecha_publicacion": "2026-06-15",
  "fecha_expiracion": "2026-07-15",
  "salario": "500000",
  "duracion": "6 meses"
}
```

---

### 📤 Respuesta exitosa

```json
{
  "message": "Oferta creada correctamente",
  "id": "uuid-generado"
}
```

---

## ❌ Errores

### 400 - Campos faltantes

```json
{
  "error": "Faltan campos obligatorios",
  "missing": ["titulo", "empresa", "link"]
}
```

---

### 500 - Error interno

```json
{
  "error": "Error al crear oferta",
  "details": "mensaje técnico"
}
```

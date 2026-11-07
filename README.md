# 🎓 Nizam College - E-Certificate System

A web-based **E-Certificate Generation and Verification System** designed for **Nizam College (Osmania University, Hyderabad)**. 

This portal enables administrators to seamlessly issue digital certificates with embedded QR codes and allows students or third parties to instantly verify the authenticity of issued certificates online.

---

## 🌟 Key Features

* **🛡️ Real-Time Certificate Verification:** Public lookup portal allowing users to verify certificates instantly by ID or by scanning an embedded QR code.
* **⚡ Admin Dashboard:** Intuitive interface for administrators to generate, track, and manage issued e-certificates.
* **📄 Automated PDF Generation:** Direct browser viewing, printing, and downloading of official PDF certificates.
* **🔐 Secure Authentication:** Protected admin login portal to ensure only authorized personnel can generate new credentials.
* **🎨 Modern Responsive UI:** Built using **Bootstrap 5**, **FontAwesome 6**, and customized with Nizam College’s institutional color theme (Navy & Gold).

---

## 📂 Project Structure

```text
.
├── templates/
│   ├── index.html         # Public Verification Portal Home
│   ├── login.html         # Admin Authentication Page
│   ├── admin.html         # Admin Dashboard & Generation Form
│   ├── certificate.html   # Certificate Viewer & Action Hub
│   └── verify.html        # Verification Result Page (Valid / Invalid)
└── README.md              # Project Documentation
```

---

## 🗂️ Overview of Page Components

| File | Description |
| :--- | :--- |
| **`index.html`** | Public landing page featuring a search box for manual certificate ID lookup and step-by-step verification instructions. |
| **`login.html`** | Secure login portal for administrative staff to access the management dashboard. |
| **`admin.html`** | Complete administration suite providing total issuance stats, interactive issuance forms, and recent records. |
| **`certificate.html`** | Dedicated page displaying the generated certificate PDF embed alongside options to print, download, or re-verify. |
| **`verify.html`** | Dynamic verification result view displaying authenticity status, recipient details, and integrity check markers. |

---

## 🛠️ Tech Stack & Dependencies

* **Frontend:** HTML5, CSS3, JavaScript (ES6)
* **CSS Framework:** [Bootstrap 5.3.3](https://getbootstrap.com/)
* **Iconography:** [Font Awesome 6.5.0](https://fontawesome.com/)
* **Backend Integration:** Compatible with Python (Flask / Django) utilizing Jinja2 templating variables (e.g., `{{ cert.name }}`, `{% for cert in certificates %}`).

---

## 🚀 Getting Started

### 1. Prerequisites
Ensure you have a backend server configured (such as **Flask** or **Django**) to render the Jinja2 templates and serve the API routes referenced in the HTML:
* `POST /login`
* `POST /generate`
* `GET /verify/<cert_id>`
* `GET /download/<cert_id>`
* `GET /pdf/<cert_id>`

### 2. Local Setup
1. Clone this repository:
   ```bash
   git clone https://github.com/your-username/nizam-college-ecertificate-system.git
   cd nizam-college-ecertificate-system
   ```
2. Place the `.html` files inside your application's `templates/` directory.
3. Start your backend application server to test the dynamic routes.

---

## 📜 How Verification Works

1. **Locate Certificate ID:** Find the unique ID printed at the bottom of the certificate (e.g., `NC-A1B2-C3D4-E5F6`).
2. **Enter or Scan:** Input the ID directly into the portal at `/` or scan the embedded QR code on the physical/digital document.
3. **Instant Validation:** The backend cross-references the record against the database and displays the validation status instantly at `/verify/<id>`.

---

## 🏫 About Nizam College

**Nizam College** is one of the oldest and most prestigious institutions of higher education in South India, constituent to **Osmania University**, Hyderabad, Telangana.

---

## 📄 License

This project is created for educational and institutional administrative use. Feel free to modify and distribute according to your organization's guidelines.

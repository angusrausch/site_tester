# 🚀 SITE TESTER

**Quick and dirty load testing for your website — see how it performs when the pressure’s on!**

---

## 🔥 What is Site Tester?

Site Tester is a lightweight, no-nonsense tool designed to help you stress test your website quickly and easily. Spin it up with Docker, fire off multiple requests, and see how your site holds up under load — all without complicated setup.

---

## ⭐ Features

- Load test any website URL
- Follow local links for deeper testing
- Control number of requests and concurrency
- Dockerized for easy setup and portability
- Simple command-line interface  
- More features planned: detailed reporting, custom headers, scheduling, and more!

---

## 🐳 Getting Started with Docker

### Build the Docker Image
```
docker build -t site_test .
```

### Run the Container
```
docker run site_test {args}
```

### Available Parameters
| Flag    | Description                        |
|---------|----------------------------------|
| `--url` | Target URL to test               |
| `-f`    | Follow local links on the site    |
| `-n`    | Number of requests to perform     |
| `-p`    | Number of concurrent workers      |
| `--type`| Type of request ["get", "post"]   |

---

## 💡 Usage Examples

- Test example.com with 100 requests and 10 concurrent workers
```
docker run site_test --url https://example.com -n 100 -p 10
```

- Test a site and follow local links
```
docker run site_test --url https://example.com -f -n 50
```

---

## 🤝 Contributing

Contributions are very welcome! Please follow these steps:

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Commit your changes (`git commit -m 'Add some feature'`)
4. Push to the branch (`git push origin feature/my-feature`)
5. Open a Pull Request

Please include clear descriptions and tests where possible.

---

## 📬 Contact / Support

If you have questions, ideas, or run into issues, feel free to open an issue.

---

## ⚠️ Important

**Only use Site Tester on websites you own or have explicit permission to test. Unauthorized load testing can cause serious issues and may be illegal.**

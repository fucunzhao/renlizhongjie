const form = document.querySelector("#applicantForm");
const successBox = document.querySelector("#successBox");

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options
  });
  const payload = await response.json();
  if (!response.ok) throw new Error(payload.error || "提交失败");
  return payload;
}

function toWorkerPayload(formData) {
  const rawTags = formData.get("tags") || "";
  const housing = formData.get("housing") || "";
  const tags = rawTags
    .split(/[,，]/)
    .map(item => item.trim())
    .filter(Boolean);
  if (housing) tags.push(housing);

  return {
    name: formData.get("name").trim(),
    phone: formData.get("phone").trim(),
    gender: formData.get("gender"),
    age: formData.get("age"),
    location: formData.get("location").trim(),
    available: formData.get("available").trim(),
    period: formData.get("period"),
    expectedRole: formData.get("expectedRole").trim(),
    salary: formData.get("salary").trim(),
    score: 75,
    tags,
    note: formData.get("note").trim(),
    source: "求职者自助登记"
  };
}

form.addEventListener("submit", async event => {
  event.preventDefault();
  const submitButton = form.querySelector("button[type='submit']");
  submitButton.disabled = true;
  submitButton.textContent = "提交中...";
  successBox.classList.remove("show");

  try {
    await api("/api/workers", {
      method: "POST",
      body: JSON.stringify(toWorkerPayload(new FormData(form)))
    });
    form.reset();
    successBox.classList.add("show");
  } catch (error) {
    successBox.textContent = `提交失败：${error.message}`;
    successBox.classList.add("show");
  } finally {
    submitButton.disabled = false;
    submitButton.textContent = "提交登记";
  }
});

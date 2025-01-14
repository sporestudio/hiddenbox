document.addEventListener("DOMContentLoaded", () => {
    const uploadForm = document.getElementById("upload-form");
    const fileInput = document.getElementById("file-input");
    const filesList = document.getElementById("files-list");

    // Fetch available files
    const fetchFiles = async () => {
        const response = await fetch("/files"); // Endpoint para obtener lista de archivos
        const files = await response.json();
        filesList.innerHTML = files.map(file => `
            <li>
                ${file.filename} 
                <a href="/download/${file.id}" target="_blank">Download</a>
            </li>
        `).join("");
    };

    // Upload a file
    uploadForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const formData = new FormData();
        formData.append("file", fileInput.files[0]);

        const response = await fetch("/upload", {
            method: "POST",
            body: formData,
        });

        if (response.ok) {
            alert("File uploaded successfully!");
            fetchFiles();
        } else {
            alert("Failed to upload file.");
        }
    });

    fetchFiles();
});

document.getElementById('upload-form').addEventListener('submit', function(e) {
    e.preventDefault();  

    const fileInput = document.getElementById('file-input');
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    fetch('/upload', {
        method: 'POST',
        body: formData,
    })
    .then(response => response.json())
    .then(data => {
        const resultDiv = document.getElementById('result');
        
        if (data.similarity_percentage !== undefined) {
          
            resultDiv.style.display = 'block';
            document.getElementById('similarity').textContent = `Similarity: ${data.similarity_percentage.toFixed(2)}%`;
            document.getElementById('comparison-text').textContent = JSON.parse(data.comparison_text).join("\n\n");
        } else {
            alert("Error: " + data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert("There was an error ");
    });
});

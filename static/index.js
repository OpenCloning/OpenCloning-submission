function setSuccessMessage(contentDiv, pull_request_url) {
    // Create a text node for the first part of the message
    const messagePart1 = document.createTextNode('🎉🎉 Your submission was successful! 🎉🎉 ');
    contentDiv.appendChild(messagePart1);

    // Create a <br> element
    const lineBreak = document.createElement('br');
    contentDiv.appendChild(lineBreak);

    // Create a text node for the second part of the message
    const messagePart2 = document.createTextNode('You can check the status of your submission ');
    contentDiv.appendChild(messagePart2);

    // Create an <a> element
    const link = document.createElement('a');
    link.href = pull_request_url;
    link.target = '_blank';
    link.textContent = 'here';
    contentDiv.appendChild(link);

    // Create a text node for the final part of the message
    const messagePart3 = document.createTextNode('.');
    contentDiv.appendChild(messagePart3);
}
async function submitFunction(e) {
    e.preventDefault();
    const loading = document.getElementById('loading')
    const errorAlert = document.querySelector('.alert-danger')
    const successMessage = document.querySelector('.alert-success')
    document.getElementById('success-message').innerHTML = ''
    try {
        errorAlert.hidden = true
        successMessage.hidden = true
        loading.hidden = false
        const { pull_request_url } = await validateZipFile()
        successMessage.hidden = false
        successMessage.innerHTML = ''
        setSuccessMessage(successMessage, pull_request_url)
    } catch (e) {
        errorAlert.hidden = false
        errorAlert.innerText = e
    }
    finally {
        loading.hidden = true
    }
}
function constrainInputFiles() {
    document.getElementById('submitted-file').addEventListener('change', function (e) {
        const files = Array.from(this.files);
        // Among the files, there should be one xlsx file and the rest should be images
        const fileExtensions = Array.from(files).map(file => file.name.split('.').pop().toLowerCase());
        const imageExtensions = ['png', 'jpg', 'jpeg', 'svg'];
        const alertMessage = `Please submit only images in format ${imageExtensions.join(', ')} and a single .xlsx file named submission.xlsx`
        if (
            // Make sure submission.xlsx is in the list
            (!files.map(f => f.name).includes('submission.xlsx')) ||
            // Make sure there is only one xlsx file
            (fileExtensions.filter(ext => ext === 'xlsx').length !== 1) ||
            // Make sure there are no other file types
            (fileExtensions.filter(ext => ext !== 'xlsx' && !imageExtensions.includes(ext)).length > 0)
        ) {
            alert(alertMessage);
            this.value = '';
        }
    });
}

async function validateZipFile() {
    const files = Array.from(document.getElementById('submitted-file').files);
    const formData = new FormData();
    files.forEach(file => {
        formData.append('files', file);
    });

    let response;
    try {
        response = await fetch('/validate_addgene_zip', {
            method: 'POST',
            body: formData
        });
    } catch (e) {
        throw new Error(e)
    }
    if (!response.ok) {
        let detail
        try {
            data = await response.json();
            detail = data.detail;
        }
        catch (e) {

            throw new Error('Internal server error.')
        }
        throw new Error(detail);
    }
    return response.json();
}

window.onload = () => {
    constrainInputFiles()
    document
        .getElementById("main-form")
        .addEventListener("submit", submitFunction);
};
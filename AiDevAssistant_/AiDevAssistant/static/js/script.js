// Handle file upload and form submission
document.addEventListener('DOMContentLoaded', function() {
    // Get the file input element
    const fileInput = document.getElementById('file');
    
    // Add an event listener to the form
    const form = document.querySelector('form');
    if (form) {
        form.addEventListener('submit', function(event) {
            // Check if a file is selected
            if (fileInput && !fileInput.files.length) {
                event.preventDefault();
                alert('Please select a file to upload.');
                return;
            }
            
            // Check file type
            if (fileInput && fileInput.files.length) {
                const file = fileInput.files[0];
                if (!file.name.toLowerCase().endsWith('.txt')) {
                    event.preventDefault();
                    alert('Please upload a .txt file.');
                    return;
                }
            }
            
            // Show loading spinner
            const submitButton = this.querySelector('button[type="submit"]');
            if (submitButton) {
                submitButton.innerHTML = '<i class="fas fa-spinner loading-spinner me-2"></i>Processing...';
                submitButton.disabled = true;
            }
        });
    }
    
    // Add animation to cards
    const cards = document.querySelectorAll('.card:not(.no-hover)');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.classList.add('shadow');
        });
        card.addEventListener('mouseleave', function() {
            this.classList.remove('shadow');
        });
    });
    
    // Add a listener to dismiss alerts automatically
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const closeButton = alert.querySelector('.btn-close');
            if (closeButton) {
                closeButton.click();
            }
        }, 5000);
    });
});

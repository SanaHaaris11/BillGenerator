// static/js/scripts.js

document.addEventListener('DOMContentLoaded', function() {
    // --- JavaScript for Dynamic Bill Item Addition/Removal (from generate_bill.html) ---
    const addItemButton = document.getElementById('add-item');
    const billItemsContainer = document.getElementById('bill-items-container');

    if (addItemButton && billItemsContainer) {
        addItemButton.addEventListener('click', function() {
            // Clone the first (or any existing) item row
            const existingRow = billItemsContainer.querySelector('.bill-item-row');
            if (!existingRow) {
                console.error("No existing bill-item-row found to clone.");
                return;
            }
            const newItemRow = existingRow.cloneNode(true);

            // Clear values in cloned row for new input
            newItemRow.querySelectorAll('input').forEach(input => input.value = '');

            // Attach event listener to the new remove button
            const removeButton = newItemRow.querySelector('.remove-item');
            if (removeButton) {
                removeButton.addEventListener('click', function() {
                    newItemRow.remove(); // Remove the parent row
                    checkMinItems(); // Check if we need to disable remove button
                });
            }

            billItemsContainer.appendChild(newItemRow);
            checkMinItems(); // Check if we need to enable remove buttons
        });

        // Add event listeners to initial remove buttons (for rows already present on page load)
        // This ensures existing rows can also be removed if there's more than one
        billItemsContainer.querySelectorAll('.remove-item').forEach(button => {
            button.addEventListener('click', function() {
                button.closest('.bill-item-row').remove();
                checkMinItems(); // Check if we need to disable remove button
            });
        });

        // Function to disable remove button if only one item row remains
        function checkMinItems() {
            const allRemoveButtons = billItemsContainer.querySelectorAll('.remove-item');
            if (allRemoveButtons.length <= 1) {
                allRemoveButtons.forEach(button => button.disabled = true);
            } else {
                allRemoveButtons.forEach(button => button.disabled = false);
            }
        }

        // Call initially to set correct state
        checkMinItems();
    }

    // --- Placeholder for AJAX Form Submissions (e.g., for add_customer, generate_bill) ---
    // In a real application, you'd use fetch() or XMLHttpRequest here
    // to send form data to your Flask backend without a full page reload.

    // Example for a generic form submission handler (requires specific form IDs/classes)
    /*
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        if (!form.classList.contains('no-ajax')) { // Add a class 'no-ajax' to forms you want to submit normally
            form.addEventListener('submit', function(event) {
                event.preventDefault(); // Prevent default form submission

                const formData = new FormData(form);
                const actionUrl = form.action; // Get the URL to submit to

                fetch(actionUrl, {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json()) // Assuming your Flask app returns JSON
                .then(data => {
                    if (data.success) {
                        alert('Operation successful: ' + data.message);
                        // Optionally redirect or update part of the page
                        if (data.redirect_url) {
                            window.location.href = data.redirect_url;
                        }
                    } else {
                        alert('Operation failed: ' + data.message);
                    }
                })
                .catch(error => {
                    console.error('Error during form submission:', error);
                    alert('An error occurred during submission.');
                });
            });
        }
    });
    */
});
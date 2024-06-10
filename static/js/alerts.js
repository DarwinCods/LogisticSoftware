// alerts.js

function showAlert(category, message) {
    var alertType = '';
    if (category === 'success') {
        alertType = 'success';
    } else if (category === 'info') {
        alertType = 'info';
    } else if (category === 'warning') {
        alertType = 'warning';
    } else if (category === 'danger') {
        alertType = 'danger';
    }
    alert(message);
}


document.getElementById('factButton').addEventListener('click', function() {
    document.getElementById('popupContainer').style.display = 'block';
});

document.getElementById('closePopup').addEventListener('click', function() {
    document.getElementById('popupContainer').style.display = 'none';
});

document.getElementById('popupButton').addEventListener('click', function() {
    var popupInputValue = document.getElementById('popupInput').value;
    alert('You entered: ' + popupInputValue);
    
});

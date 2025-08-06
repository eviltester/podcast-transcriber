function postCallFromButton(aButton,anEndPoint,aBody){

    aButton.disabled = true;

    fetch(anEndPoint, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: aBody
    })
    .then(response => response.json())
    .then(data => {
        alert('Success: ' + JSON.stringify(data));
    })
    .catch((error) => {
        alert('Error: ' + error);
    })
    .finally(() => {
        aButton.disabled = false;
    });

}
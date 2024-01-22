function validateForm() {
    var age = document.getElementById('age').value;
    var weight = document.getElementById('weight').value;
    var height = document.getElementById('height').value;

    if (age === "" || weight === "" || height === "") {

        var emptyFields = [];

        if (age === "") {
            emptyFields.push("Age");}
        if (weight === "") {
            emptyFields.push("Weight");}
        if (height === "") {
            emptyFields.push("Height");}

        var message = "Please fill out the following fields:\n" + emptyFields.join("\n");
        alert(message);
        return false;
    }
    return true;
}
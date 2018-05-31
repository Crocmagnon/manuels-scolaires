document.addEventListener("DOMContentLoaded", function (event) {
    var _selector = document.querySelector('#id_no_book');
    _selector.addEventListener('change', function (event) {
        if (_selector.checked) {
            document.querySelector('#id_title').value = "PAS DE LIVRE POUR CETTE CLASSE";
            document.querySelector('#id_authors').value = "N/A";
            document.querySelector('#id_editor').value = 1;
            document.querySelector('#id_publication_year').value = 1900;
            document.querySelector('#id_isbn').value = "0000000000";
            document.querySelector('#id_price').value = 0;
        } else {
            document.querySelector('#id_title').value = "";
            document.querySelector('#id_authors').value = "";
            document.querySelector('#id_editor').value = "";
            document.querySelector('#id_publication_year').value = "";
            document.querySelector('#id_isbn').value = "";
            document.querySelector('#id_price').value = "";
        }
    });
});

document.addEventListener("DOMContentLoaded", function (event) {
    var _selector = document.querySelector('#id_no_book');
    if (_selector === null) return;
    var data = {
        title: document.querySelector('#id_title').value,
        authors: document.querySelector('#id_authors').value,
        publicationYear: document.querySelector('#id_publication_year').value,
        isbn: document.querySelector('#id_isbn').value,
        price: document.querySelector('#id_price').value,
        editor: document.querySelector('#id_editor').value,
    };
    _selector.addEventListener('change', function (event) {
        if (_selector.checked) {
            data = {
                title: document.querySelector('#id_title').value,
                authors: document.querySelector('#id_authors').value,
                publicationYear: document.querySelector('#id_publication_year').value,
                isbn: document.querySelector('#id_isbn').value,
                price: document.querySelector('#id_price').value,
                editor: document.querySelector('#id_editor').value,
            };
            document.querySelector('#id_title').value = "PAS DE LIVRE POUR CETTE CLASSE";
            document.querySelector('#id_authors').value = "N/A";
            document.querySelector('#id_publication_year').value = 1900;
            document.querySelector('#id_isbn').value = "0000000000";
            document.querySelector('#id_price').value = 0;
            var editorValue = null;
            for (var option of document.querySelector('#id_editor').children) {
                if (editorValue === null && option.value !== "") {
                    editorValue = option.value;
                }
                if (option.firstChild.data.toLowerCase().indexOf('autre') !== -1) {
                    editorValue = option.value;
                }
            }
            document.querySelector('#id_editor').value = editorValue;
        } else {
            document.querySelector('#id_title').value = data.title;
            document.querySelector('#id_authors').value = data.authors;
            document.querySelector('#id_editor').value = data.editor;
            document.querySelector('#id_publication_year').value = data.publicationYear;
            document.querySelector('#id_isbn').value = data.isbn;
            document.querySelector('#id_price').value = data.price;
        }
    });
});

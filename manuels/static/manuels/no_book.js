document.addEventListener("DOMContentLoaded", function (event) {
    var selectors = [
        {
            id: "#id_no_book",
            value: "PAS DE LIVRE POUR CETTE CLASSE"
        },
        {
            id: "#id_see_later",
            value: "VOIR À LA RENTRÉE"
        },
    ];
    selectors.forEach(function (selector, index, array) {
        var _selector = document.querySelector(selector.id);
        if (_selector === null) return;
        var data = {
            title: document.querySelector('#id_title').value,
            authors: document.querySelector('#id_authors').value,
            publicationYear: document.querySelector('#id_publication_year').value,
            isbn: document.querySelector('#id_isbn').value,
            price: document.querySelector('#id_price').value,
            editor: document.querySelector('#id_editor').value,
            previouslyAcquired: document.querySelector('#id_previously_acquired').value,
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
                    previouslyAcquired: document.querySelector('#id_previously_acquired').value,
                };
                document.querySelector('#id_title').value = selector.value;
                document.querySelector('#id_authors').value = "N/A";
                document.querySelector('#id_publication_year').value = 1900;
                document.querySelector('#id_isbn').value = "0000000000";
                document.querySelector('#id_price').value = 0;
                document.querySelector('#id_previously_acquired').value = "False";
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
                document.querySelector('#id_previously_acquired').value = data.previouslyAcquired;
            }
        });
    });


    function toggleOtherEditorDisplay() {
        var editor = document.querySelector('#id_editor');
        var otherEditor = document.querySelector('#id_other_editor').parentElement;

        if (editor.options[editor.selectedIndex].text.toLowerCase().indexOf('autre') !== -1) {
            otherEditor.style.display = 'block';
        }
        else {
            otherEditor.style.display = 'none';
        }
    }
    toggleOtherEditorDisplay();

    document.querySelector('#id_editor').addEventListener('change', toggleOtherEditorDisplay);

});

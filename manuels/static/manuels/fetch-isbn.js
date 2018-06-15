document.addEventListener("DOMContentLoaded", function (event) {
    var isbnButton = document.querySelector('#id_isbn_button');
    var isbn = document.querySelector('#id_isbn');
    isbnButton.addEventListener('click', function (event) {
        $.get("/isbn_api/" + isbn.value, {}, function (data, status, xhr) {
            if (data.error) {
                isbn.classList.add('is-invalid');
                isbn.classList.remove('is-valid');
                document.querySelector('#id_isbn_invalid_feedback').style.display = 'block';
                document.querySelector('#id_isbn_error_text').textContent = data.error;
                return;
            }

            isbn.classList.remove('is-invalid');
            isbn.classList.add('is-valid');
            document.querySelector('#id_isbn_invalid_feedback').style.display = 'none';

            document.querySelector('#id_title').value = data.title;
            document.querySelector('#id_title').classList.add('is-valid');
            document.querySelector('#id_authors').value = data.authors;
            document.querySelector('#id_authors').classList.add('is-valid');
            document.querySelector('#id_publication_year').value = data.year;
            document.querySelector('#id_publication_year').classList.add('is-valid');
            document.querySelector('#id_price').value = data.price;
            document.querySelector('#id_price').classList.add('is-valid');

            var editorValue = "";
            var editorIsOther = false;
            for (var option of document.querySelector('#id_editor').children) {
                if (editorValue === "" && option.firstChild.data.toLowerCase().indexOf('autre') !== -1) {
                    editorValue = option.value;
                    editorIsOther = true;
                }
                if (option.firstChild.data.toLowerCase() === data.editor.toLowerCase()) {
                    editorValue = option.value;
                    editorIsOther = false;
                }
            }
            document.querySelector('#id_editor').value = editorValue;
            document.querySelector('#id_editor').classList.add('is-valid');

            event = document.createEvent("HTMLEvents");
            event.initEvent("change", true, true);
            event.eventName = "change";
            document.querySelector('#id_editor').dispatchEvent(event);
            if (editorIsOther) {
                document.querySelector('#id_other_editor').value = data.editor;
                document.querySelector('#id_other_editor').classList.add('is-valid');
            }
        });
    });
});

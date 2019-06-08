document.addEventListener("DOMContentLoaded", function (event) {
    $(function () {
      $('[data-toggle="tooltip"]').tooltip();
    });

    var isbnButton = document.querySelector('#id_isbn_button');
    var isbn = document.querySelector('#id_isbn');
    var title = document.querySelector('#id_title');
    var authors = document.querySelector('#id_authors');
    var year = document.querySelector('#id_publication_year');
    var price = document.querySelector('#id_price');
    var editor = document.querySelector('#id_editor');
    var otherEditor = document.querySelector('#id_other_editor');
    var spinner = document.querySelector('#id_isbn_spinner');
    var feedback = document.querySelector('#id_isbn_invalid_feedback');

    function enableFields() {
        isbn.removeAttribute('disabled');
        isbnButton.removeAttribute('disabled');
        document.querySelector('#id_title').removeAttribute('disabled');
        authors.removeAttribute('disabled');
        year.removeAttribute('disabled');
        price.removeAttribute('disabled');
        editor.removeAttribute('disabled');
        otherEditor.removeAttribute('disabled');
        spinner.setAttribute('hidden', 'hidden');
    }

    function disableFields() {
        isbn.setAttribute('disabled', 'disabled');
        isbnButton.setAttribute('disabled', 'disabled');
        title.setAttribute('disabled', 'disabled');
        authors.setAttribute('disabled', 'disabled');
        year.setAttribute('disabled', 'disabled');
        price.setAttribute('disabled', 'disabled');
        editor.setAttribute('disabled', 'disabled');
        otherEditor.setAttribute('disabled', 'disabled');
        spinner.removeAttribute('hidden');
    }

    isbnButton.addEventListener('click', function (event) {
        if (!isbn.value) {
            return;
        }
        disableFields();

        $.get("/isbn_api/" + isbn.value, {}, function (data, status, xhr) {
            if (data.error) {
                isbn.classList.add('is-invalid');
                isbn.classList.remove('is-valid');
                feedback.style.display = 'block';
                feedback.textContent = data.error;
                enableFields();
                return;
            }

            isbn.classList.remove('is-invalid');
            isbn.classList.add('is-valid');
            feedback.style.display = 'none';
            feedback.textContent = '';

            title.value = data.title;
            title.classList.add('is-valid');
            authors.value = data.authors;
            authors.classList.add('is-valid');
            year.value = data.year;
            year.classList.add('is-valid');
            price.value = data.price;
            price.classList.add('is-valid');

            var editorValue = "";
            var editorIsOther = false;
            if (data.editor) {
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
            }
            editor.value = editorValue;
            editor.classList.add('is-valid');

            if (editorIsOther) {
                otherEditor.value = data.editor;
                otherEditor.classList.add('is-valid');
            }
            enableFields();

            // The event propagation must be done after the fields have been re-enabled
            // because a change event can't be propagated to a field that's disabled.
            var event = document.createEvent("HTMLEvents");
            event.initEvent("change", true, true);
            event.eventName = "change";
            document.querySelector('#id_editor').dispatchEvent(event);
        });
    });
});

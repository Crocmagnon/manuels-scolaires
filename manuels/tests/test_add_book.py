from manuels.tests.selenium import TeacherSeleniumTestCase


class AddBookTestCase(TeacherSeleniumTestCase):
    def test_add_book_with_decitre(self):
        # empty cache
        # use vcrpy to reproduce decitre call on a known book
        # Click on add book button
        # select level
        # fill discipline
        # fill ISBN
        # click on "fill with decitre"
        # check info is filled
        # check values, especially price
        # finish filling form
        # check book is created
        assert False

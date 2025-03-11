#!/usr/bin/env python3
"""
Handler class for Google Form duration questions.

This script allows for the standardised handling of the Google Form duration questions.

Usage:
    To get question metadata while checking for success/failure: if not DurationQuestion.get_info(): ...
    To answer the question: DurationQuestion.answer(hour, minute, second)
"""

from browser import Browser
import logging
from questions import BaseQuestion
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from typing import Optional, Tuple

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
_logger = logging.getLogger(__name__)


class DurationQuestion(BaseQuestion):
    """
    DurationQuestion class as a Google Form duration question wrapper.

    This script caches the hour, minute and second input fields used for answering and awaits user input.
    It also validates hour, minute and second user input before submission of duration answer.

    Attributes
        _HEADER             The Google Form question header (title); also serves as the UID for the question class.
        _DESCRIPTION        The Google Form question description.
        _REQUIRED           The required flag for the Google Form question.
        _QUESTION_ELEMENT   The web element in the Google Form which represents the entire Google Form question.
        _ANSWER_ELEMENTS    The web element(s) in the Google Form which are used to answer the Google Form question.
        _BROWSER            The selenium browser instance used to host the Google Form.
    """

    # Define constants
    _DURATION_HOUR_ARIA_LABEL = "Hours"
    _DURATION_MINUTE_ARIA_LABEL = "Minutes"
    _DURATION_SECOND_ARIA_LABEL = "Seconds"

    # region Getters and Setters

    @classmethod
    def get_hour_label(cls) -> str:
        """Helper function to get the hour web element aria label.

        :return: The hour web element aria label.
        """

        return cls._DURATION_HOUR_ARIA_LABEL

    @classmethod
    def get_minute_label(cls) -> str:
        """Helper function to get the minute web element aria label.

        :return: The minute web element aria label.
        """

        return cls._DURATION_MINUTE_ARIA_LABEL

    @classmethod
    def get_second_label(cls) -> str:
        """Helper function to get the second web element aria label.

        :return: The second web element aria label.
        """

        return cls._DURATION_SECOND_ARIA_LABEL

    def get_answer_elements(self) -> Optional[Tuple[WebElement, WebElement, WebElement]]:
        """Gets the web elements for the hour, minute and second input fields.

        :return: (Web element for the hour input field,
                  web element for the minute input field,
                  web element for the second input field), if it has been successfully set.
        """

        if not self._ANSWER_ELEMENTS:
            _logger.warning("DurationQuestion trying to get answer element that has not been set")
        return self._ANSWER_ELEMENTS

    def set_answer_elements(self, hour_element: WebElement, minute_element: WebElement,
                            second_element: WebElement) -> None:
        """Sets the web element for the hour, minute and second input fields if it has changed.

        :param hour_element: The web element for the hour input field.
        :param minute_element: The web element for the minute input field.
        :param second_element: The web element for the second input field.
        """

        self._ANSWER_ELEMENTS = hour_element, minute_element, second_element

    # endregion Getters and Setters

    @Browser.monitor_browser
    def get_info(self) -> Optional[bool]:
        """Obtains question metadata from Google Form.

        :return: True if the question metadata has been successfully cached, False otherwise.
                 Returns None only if Browser.monitor_browser returns None.
        """

        result = super().get_info()
        if not result:
            # Cascade the unwanted result
            return result

        self.set_answer_elements(
            # Obtain the hour element
            self._QUESTION_ELEMENT.find_element(By.XPATH,
                ".//input[@aria-label='{}']".format(self._DURATION_HOUR_ARIA_LABEL)),
            # Obtain the minute element
            self._QUESTION_ELEMENT.find_element(By.XPATH,
                ".//input[@aria-label='{}']".format(self._DURATION_MINUTE_ARIA_LABEL)),
            # Obtain the second element
            self._QUESTION_ELEMENT.find_element(By.XPATH,
                ".//input[@aria-label='{}']".format(self._DURATION_SECOND_ARIA_LABEL))
        )
        return True

    def answer(self, duration: str) -> Optional[bool]:
        """Answers the question with specified user input.

        For duration, the maximum number of hours allowed is 72.

        :param duration: The duration answer to the question.
                         The duration answer is expected to be of format "%H:%M:%S".
        :return: True if the question is answered successfully, False if a sanity check fails,
                 and None if _perform_submission returns None.
        """

        # Sanity check
        if not (bool(self.get_answer_elements()) and self._is_valid(*self._ANSWER_ELEMENTS)):
            result = self.get_info()
            if not result:
                # Cascade unwanted result
                return result

        # Ensure valid inputs
        try:
            hour, minute, second = duration.split(":")
            hour, minute, second = int(hour), int(minute), int(second)
            if not (0 <= hour <= 72 and 0 <= minute <= 59 and 0 <= second <= 59):
                raise ValueError
        except ValueError:
            _logger.error("%s trying to answer a duration with duration=%s", self.__class__.__name__, duration)
            return False
        assert bool(isinstance(val, int) for val in (hour, minute, second))

        # Send instructions to Google Forms
        for element, answer in zip(self._ANSWER_ELEMENTS, (hour, minute, second)):
            element.click()
            element.send_keys(answer)
        return True


if __name__ == '__main__':
    pass

# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.game import Game  # noqa: E501
from swagger_server.test import BaseTestCase


class TestGamesController(BaseTestCase):
    """GamesController integration test stubs"""

    def test_games_get(self):
        """Test case for games_get

        Get a list of games
        """
        response = self.client.open(
            '/games',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_games_id_delete(self):
        """Test case for games_id_delete

        Delete a game by ID
        """
        response = self.client.open(
            '/games/{id}'.format(id=56),
            method='DELETE')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_games_id_get(self):
        """Test case for games_id_get

        Get a game by ID
        """
        response = self.client.open(
            '/games/{id}'.format(id=56),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_games_id_put(self):
        """Test case for games_id_put

        Update a game by ID
        """
        body = Game()
        response = self.client.open(
            '/games/{id}'.format(id=56),
            method='PUT',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_games_post(self):
        """Test case for games_post

        Add a new game
        """
        body = Game()
        response = self.client.open(
            '/games',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()

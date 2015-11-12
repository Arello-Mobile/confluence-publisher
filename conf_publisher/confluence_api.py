import requests
from . import log
from .constants import DEFAULT_CONFLUENCE_API_VERSION


def create_confluence_api(version, url, auth):
    # Documentation for different REST API versions: https://docs.atlassian.com/confluence/REST/

    confluence_api_class = None
    if version == DEFAULT_CONFLUENCE_API_VERSION:
        confluence_api_class = ConfluenceRestApi553

    if confluence_api_class is None:
        raise NotImplementedError('This API Version is not implemented')

    confluence_api = confluence_api_class(url, auth)

    return confluence_api


class ConfluenceRestApiBase(object):
    api_path = 'rest/api'

    def __init__(self, url, auth):
        self.confluence_url = url.rstrip('/')
        self.auth = auth
        self.headers = {
            'content-type': 'application/json',
            'Authorization': 'Basic ' + auth
        }

    @staticmethod
    def _build_params(params_map):
        return dict((k, v) for k, v in params_map.items() if v is not None)

    def _construct_url(self, *url_parts):
        parts = [str(part) for part in url_parts]
        return '/'.join([self.confluence_url, self.api_path] + parts)

    def _get(self, url, **kwargs):
        return self._request(requests.get, url, **kwargs)

    def _post(self, url, _json=None, **kwargs):
        return self._request(requests.post, url, json=_json, **kwargs)

    def _put(self, url, _json=None, **kwargs):
        return self._request(requests.put, url, json=_json, **kwargs)

    def _delete(self, url, **kwargs):
        return self._request(requests.delete, url, **kwargs)

    def _request(self, requester, url, **kwargs):
        if 'headers' not in kwargs:
            kwargs['headers'] = self.headers

        log.debug('Request URL: %s', url)
        log.debug('Request Arguments: %s', kwargs)

        r = requester(url, **kwargs)
        if r.status_code != requests.codes.ok:
            log.error(r.content)
            r.raise_for_status()

        ret = r.json()

        log.debug('Request Response: %s', ret)

        return ret


class ConfluenceRestApi553(ConfluenceRestApiBase):
    # Documentation for Confluence v5.5.3 REST API: https://docs.atlassian.com/confluence/REST/5.5.3/

    def list_content(self, space_key, type='page', title=None, posting_day=None, expand='history,space,version', start=0, limit=25):
        """
        Returns a paginated list of Content

        GET /rest/api/content?type&spaceKey&title&postingDay&expand&start&limit

        :param space_key:       the space key to find content under. Required
        :param type:            the content type to return. Default value: page. Valid values: page, blogpost. Default: page
        :param title:           the title of the page to find. Required for page type
        :param posting_day:     the posting day of the blog post. Required for blogpost type. Format: yyyy-mm-dd. Example: 2013-02-13
        :param expand:          a comma separated list of properties to expand on the content. Default value: history,space,version.
        :param start:           the start point of the collection to return
        :param limit:           the limit of the number of items to return, this may be restricted by fixed system limits. Default: 25
        :return:
        """
        params_map = {'spaceKey': space_key, 'type': type, 'title': title, 'postingDay': posting_day, 'expand': expand, 'start': start, 'limit': limit}

        url = self._construct_url('content')
        params = self._build_params(params_map)

        ret = self._get(url, params=params)
        return ret

    def get_content(self, content_id, expand='history,space,version'):
        """
        Returns a piece of Content.

        GET /rest/api/content/{id}

        :param content_id:      the id of the content
        :param expand:          A comma separated list of properties to expand on the content. Default value: history,space,version
        :return:
        """
        params_map = {'expand': expand}

        url = self._construct_url('content', content_id)
        params = self._build_params(params_map)

        ret = self._get(url, params=params)
        return ret

    def create_content(self, data):
        """
        Creates a new piece of Content.

        POST /rest/api/content

        :param data:
        :return:
        """
        url = self._construct_url('content')
        ret = self._post(url, data)
        return ret

    def update_content(self, content_id, data):
        """
        Updates a piece of Content.

        PUT /rest/api/content/{id}

        :param content_id:      the id of the content
        :return:

        The body contains the representation of the content. Must include the new version number.

        """
        url = self._construct_url('content', content_id)
        ret = self._put(url, data)
        return ret

    def delete_content(self, content_id):
        """
        Deletes a piece of Content.

        DELETE /rest/api/content/{id}

        :param content_id:      the id of the content
        :return:
        """
        url = self._construct_url('content', content_id)
        ret = self._delete(url)
        return ret

    def list_attachments(self, content_id, expand=None, start=0, limit=50, filename=None, media_type=None):
        """
        Returns a paginated list of attachment Content entities within a single container.

        GET /rest/api/content/{id}/child/attachment?expand&start&limit&filename&mediaType

        :param content_id:      a string containing the id of the attachments content container
        :param expand:          a comma separated list of properties to expand on the Attachments returned. Optional.
        :param start:           the index of the first item within the result set that should be returned. Optional.
        :param limit:           how many items should be returned after the start index. Optional. Default: 50
        :param filename:        filter parameter to return only the Attachment with the matching file name. Optional.
        :param media_type:      filter parameter to return only Attachments with a matching Media-Type. Optional.
        :return:
        """
        params_map = {'mediaType': media_type, 'filename': filename, 'expand': expand, 'start': start, 'limit': limit}

        url = self._construct_url('content', content_id, 'child', 'attachment')
        params = self._build_params(params_map)

        ret = self._get(url, params=params)
        return ret

    def create_attachment(self, content_id, attachment, comment=None, minor_edits=False):
        """
        Add one or more attachments to a Confluence Content entity, with optional comments.

        POST /rest/api/content/{id}/child/attachment

        :param content_id:      a string containing the id of the attachments content container
        :param attachment:
        :param comment:
        :param minor_edits:
        :return:
        """
        url = self._construct_url('content', content_id, 'child', 'attachment')
        ret = self._create_attachment(url, attachment, comment, minor_edits)
        return ret

    def update_attachment_data(self, content_id, attachment_id, attachment, comment=None, minor_edits=False):
        """
        Update the binary data of an Attachment, and optionally the comment.

        POST /rest/api/content/{id}/child/attachment/{attachmentId}/data

        :param content_id:      a string containing the id of the attachments content container
        :param attachment_id:   the id of the attachment to update
        :param attachment:
        :param comment:
        :param minor_edits:
        :return:
        """
        url = self._construct_url('content', content_id, 'child', 'attachment', attachment_id, 'data')
        ret = self._create_attachment(url, attachment, comment, minor_edits)
        return ret

    def _create_attachment(self, url, attachment, comment=None, minor_edits=False):
        headers = {
            'X-Atlassian-Token': 'no-check',
            'Authorization': 'Basic ' + self.auth
        }

        params_map = {'comment': comment, 'minorEdit': minor_edits}
        params = self._build_params(params_map)

        ret = self._post(url, files={'file': attachment}, data=params, headers=headers)
        return ret

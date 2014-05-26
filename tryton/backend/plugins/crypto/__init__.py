# -*- coding: utf-8 -*-
##############################################################################
#
#    GNU Health: The Free Health and Hospital Information System
#    Copyright (C) 2008-2014 Luis Falcon <lfalcon@gnusolidario.org>
#    Copyright (C) 2011-2014 GNU Solidario <health@gnusolidario.org>
#
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import tryton.rpc as rpc
from tryton.common import RPCExecute, warning, message
from tryton.gui.window.form import Form
import gettext
import gnupg

_ = gettext.gettext


def sign_document(data):
    """ Retrieve the hash value of the serialized document and
        generates a clearsign signature using the user's private key
        on the client side via GNU Privacy Guard - GPG -"""

    gpg = gnupg.GPG()

    document_model = data['model']

    """ Don't allow signing more than one document at a time
        To avoid signing unwanted / unread documents
    """

    if (len(data['ids']) > 1):
        warning(
            _('For security reasons, Please sign one document at a time'),
            _('Multiple records selected !'),
        )
        return

    """ Verify that the document handles digital signatures """

    try:
        record_vals = rpc.execute(
            'model', document_model, 'read',
            data['ids'],
            ['document_digest', 'digital_signature'], rpc.CONTEXT)

    except:
        warning(
            _('Please enable the model for digital signature'),
            _('No Digest or Digital Signature fields found !'),
        )
        return

    digest = record_vals[0]['document_digest']

    """ Check that the document hasn't been signed already """

    if record_vals[0]['digital_signature']:
        warning(
            _('Document already signed'),
            _('This record has been already signed'),
        )
        return

    try:
        gpg_signature = gpg.sign(digest, clearsign=True)

    except:
        warning(
            _('Error when signing the document'),
            _('Please check your encryption settings'),
        )

    """
    Set the clearsigned digest
    """
    try:
        RPCExecute(
            'model', document_model, 'set_signature',
            data, str(gpg_signature))

    except:
        warning(
            _('Error when saving the digital signature'),
            _('The signature was generated but NOT saved !'),
        )

    else:
        message(_('Document digitally signed'))

        # TODO
        # Reload the record view after storing the digital signature
        # sig_reload or other method to check.
        # a = Form(document_model, data['ids'])
        # a.sig_reload()
        # a.message_info(_('Document digitally signed'), color='blue')


def get_plugins(model):
    return [
        (_('Sign Document'), sign_document),
    ]

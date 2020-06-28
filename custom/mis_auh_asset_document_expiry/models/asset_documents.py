# -*- coding: utf-8 -*-

from odoo import models, fields


class AssetDocument(models.Model):
    _name = 'asset.document'
    _description = 'Documents Template '

    name = fields.Char(string='Document Name', required=True, copy=False, help='You can give your'
                                                                               'Document name here.')
    note = fields.Text(string='Note', copy=False, help="Note")
    attach_id = fields.Many2many('ir.attachment', 'attach_rel', 'doc_id', 'attach_id3', string="Attachment",
                                 help='You can attach the copy of your document', copy=False)


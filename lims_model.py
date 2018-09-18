# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.exceptions import  ValidationError

class LimsReactor(models.Model):
     _name = 'lims.reactor'
     name = fields.Char('Reactor Name', required=True, index=True)
     rdesc = fields.Char('Description')
     state = fields.Selection([('A','Active'),('I','Inactive')], 'State', default='A', required=True, help='Reactor State')

     _sql_constraints = [
         ('name_unique', 'unique(name)', 'Reactor already exists!')
     ]

     @api.onchange('name')
     def set_caps(self):        
	     if self.name == False or self.name == '':
		    return ''
	     else:
         	val = str(self.name)
         	self.name = val.upper()

     @api.one
     def alter_inactive(self):
	     self.state = 'I'
	     return True

     @api.one
     def alter_active(self):
         self.state = 'A'
         return True

class LimsProduct(models.Model):
    _name = 'lims.product'
    name = fields.Char('Product Name', required=True, index=True)
    pdesc = fields.Char('Description')
    state = fields.Selection([('A', 'Active'), ('I', 'Inactive')], 'State', default='A', required=True,
                             help='Product State')
    # Related model in one2many
    products = fields.One2many('lims.product.test', 'product_id', 'Referenced product')

    _sql_constraints = [
        ('name_unique', 'unique(name)', 'Product already exists!')
    ]

    @api.onchange('name')
    def set_caps(self):
        if self.name == False or self.name == '':
            return ''
        else:
            val = str(self.name)
            self.name = val.upper()

    @api.one
    def alter_inactive(self):
        self.state = 'I'
        return True

    @api.one
    def alter_active(self):
        self.state = 'A'
        return True

class LimsTest(models.Model):
    _name = 'lims.test'
    name = fields.Char('Test Name', required=True, index=True)
    tdesc = fields.Char('Description')
    unit = fields.Char('Unit', help='Unit of Measure')
    state = fields.Selection([('A', 'Active'), ('I', 'Inactive')], 'State', default='A', required=True,
                             help='Test State')
    # Related model in one2many
    test_id = fields.One2many('lims.product.test', 'test_id', string='Referenced Test')

    _sql_constraints = [
        ('name_unique', 'unique(name)', 'Test already exists!')
    ]

    @api.onchange('name')
    def set_caps(self):
        if self.name == False or self.name == '':
            return ''
        else:
            val = str(self.name)
            self.name = val.upper()

    @api.onchange('unit')
    def set_caps_unit(self):
        if self.unit == False or self.unit == '':
            return ''
        else:
            val = str(self.unit)
            self.unit = val.upper()

    @api.one
    def alter_inactive(self):
        self.state = 'I'
        return True

    @api.one
    def alter_active(self):
        self.state = 'A'
        return True

class LimsProductTest(models.Model):
    _name = 'lims.product.test'
    _order = 'product_id desc, id asc'

    product_id = fields.Many2one('lims.product', string='Product', required=True, ondelete='restrict', index=True,
                               copy=False)
    name = fields.Char(string='Description', compute='_compute_name', store=True)
    test_id = fields.Many2one('lims.test', string='Test', required=True, ondelete='restrict')
    unit = fields.Char(string='UOM', compute='_compute_uom', store=True)
    vmax = fields.Float(string='Maximum', digits=(8,2), default=0.0)
    vmin = fields.Float(string='Minimum', digits=(8,2), default=0.0)
    coa = fields.Selection([('Y', 'Yes'), ('N', 'No')], 'Print COA', default='Y', required=True,
                             help='Test result show')
    state = fields.Selection([('A', 'Active'), ('I', 'Inactive')], 'State', default='A', required=True,
                             help='State')
    flg = fields.Selection([('FP', 'Finish Product Test'), ('IP', 'In Process Test')], 'Test Flag', default='FP', required=True,
                             help='IP test items includes FP')

    _sql_constraints = [
        ('product_test_unique', 'unique(product_id,test_id)', 'Test already exists for this product!')
    ]

    @api.constrains('vmax', 'vmin')
    def _check_value(self):
        if self.vmin > self.vmax:
            raise ValidationError("Minimum should not be greater than Maximum")

    @api.one
    def alter_inactive(self):
        self.state = 'I'
        return True

    @api.one
    def alter_active(self):
        self.state = 'A'
        return True

    @api.multi
    @api.depends('test_id.unit')
    def _compute_uom(self):
        self.ensure_one()
        self.unit = self.test_id.unit

    @api.multi
    @api.depends('product_id.name', 'test_id.name')
    def _compute_name(self):
        self.ensure_one()
        names = [self.product_id.name, self.test_id.name]
        self.name = '/'.join(filter(None, names))

class LimsLot(models.Model):
    _name = "lims.lot"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _order = 'date_lot desc, id desc'

    name = fields.Char('Lot Number', required=True, index=True)

    state = fields.Selection([
        ('ip', 'In Process'),
        ('wk', 'Works'),
        ('fp', 'Final Product'),
    ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='ip')

    date_lot = fields.Datetime(string='Lot Date', required=True, readonly=True, index=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, copy=False, default=fields.Datetime.now)
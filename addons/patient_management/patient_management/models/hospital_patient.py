from odoo import api, fields, models
from odoo.exceptions import ValidationError


class HospitalPatient(models.Model):
    _name = 'hospital.patient'
    _description = 'Hospital Patient'

    name = fields.Char(string='Tên bệnh nhân', required=True)
    age = fields.Integer(string='Tuổi')
    disease = fields.Char(string='Bệnh')
    doctor_id = fields.Many2one('res.partner', string='Bác sĩ phụ trách')

    @api.constrains('age')
    def _check_age(self):
        for record in self:
            if record.age < 0:
                raise ValidationError("Tuổi không được nhỏ hơn 0!")

    _unique_patient_doctor = models.Constraint(
        'UNIQUE(name)',
        'Một bệnh nhân chỉ được đăng ký với một bác sĩ duy nhất!',
    )

    def action_update_patient(self, vals):
        """Phương thức cập nhật thông tin bệnh nhân."""
        return self.write(vals)
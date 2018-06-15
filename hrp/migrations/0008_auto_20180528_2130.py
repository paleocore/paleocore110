# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2018-05-28 21:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hrp', '0007_auto_20180528_2122'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='biology',
            name='attributes',
        ),
        migrations.RemoveField(
            model_name='biology',
            name='morphobank_number',
        ),
        migrations.RemoveField(
            model_name='biology',
            name='preparations',
        ),
        migrations.AddField(
            model_name='biology',
            name='element_number',
            field=models.CharField(blank=True, choices=[('1', '1'), ('2', '2'), ('3', '3'), ('3(medial)', '3(medial)'), ('4', '4'), ('4(lateral)', '4(lateral)'), ('5', '5'), ('6', '6'), ('7', '7'), ('8', '8'), ('9', '9'), ('10', '10'), ('11', '11'), ('12', '12'), ('13', '13'), ('14', '14'), ('15', '15'), ('16', '16'), ('17', '17'), ('2-7', '2-7'), ('8-12', '8-12'), ('indeterminate', 'indeterminate')], max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='biology',
            name='element_portion',
            field=models.CharField(blank=True, choices=[('almost complete', 'almost complete'), ('anterior', 'anterior'), ('basal', 'basal'), ('caudal', 'caudal'), ('complete', 'complete'), ('cranial', 'cranial'), ('diaphysis', 'diaphysis'), ('diaphysis+distal', 'diaphysis+distal'), ('diaphysis+proximal', 'diaphysis+proximal'), ('distal', 'distal'), ('dorsal', 'dorsal'), ('epiphysis', 'epiphysis'), ('fragment', 'fragment'), ('fragments', 'fragments'), ('indeterminate', 'indeterminate'), ('lateral', 'lateral'), ('medial', 'medial'), ('midsection', 'midsection'), ('midsection+basal', 'midsection+basal'), ('midsection+distal', 'midsection+distal'), ('posterior', 'posterior'), ('proximal', 'proximal'), ('symphysis', 'symphysis'), ('ventral', 'ventral')], max_length=50, null=True, verbose_name='Element Portion'),
        ),
        migrations.AddField(
            model_name='biology',
            name='element_remarks',
            field=models.TextField(blank=True, max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='biology',
            name='size_class',
            field=models.CharField(blank=True, choices=[('indeterminate', 'indeterminate'), ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')], max_length=50, null=True, verbose_name='Size Class'),
        ),
        migrations.AddField(
            model_name='biology',
            name='taxonomy_remarks',
            field=models.TextField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='biology',
            name='element',
            field=models.CharField(blank=True, choices=[('astragalus', 'astragalus'), ('bacculum', 'bacculum'), ('bone (indet.)', 'bone (indet.)'), ('calcaneus', 'calcaneus'), ('canine', 'canine'), ('capitate', 'capitate'), ('carapace', 'carapace'), ('carpal (indet.)', 'carpal (indet.)'), ('carpal/tarsal', 'carpal/tarsal'), ('carpometacarpus', 'carpometacarpus'), ('carpus', 'carpus'), ('chela', 'chela'), ('clavicle', 'clavicle'), ('coccyx', 'coccyx'), ('coprolite', 'coprolite'), ('cranium', 'cranium'), ('cranium w/horn core', 'cranium w/horn core'), ('cuboid', 'cuboid'), ('cubonavicular', 'cubonavicular'), ('cuneiform', 'cuneiform'), ('dermal plate', 'dermal plate'), ('egg shell', 'egg shell'), ('endocast', 'endocast'), ('ethmoid', 'ethmoid'), ('femur', 'femur'), ('fibula', 'fibula'), ('frontal', 'frontal'), ('hamate', 'hamate'), ('horn core', 'horn core'), ('humerus', 'humerus'), ('hyoid', 'hyoid'), ('Ilium', 'Ilium'), ('incisor', 'incisor'), ('innominate', 'innominate'), ('ischium', 'ischium'), ('lacrimal', 'lacrimal'), ('long bone ', 'long bone '), ('lunate', 'lunate'), ('mandible', 'mandible'), ('manus', 'manus'), ('maxilla', 'maxilla'), ('metacarpal', 'metacarpal'), ('metapodial', 'metapodial'), ('metatarsal', 'metatarsal'), ('molar', 'molar'), ('nasal', 'nasal'), ('navicular', 'navicular'), ('naviculocuboid', 'naviculocuboid'), ('occipital', 'occipital'), ('ossicone', 'ossicone'), ('parietal', 'parietal'), ('patella', 'patella'), ('pes', 'pes'), ('phalanx', 'phalanx'), ('pisiform', 'pisiform'), ('plastron', 'plastron'), ('premaxilla', 'premaxilla'), ('premolar', 'premolar'), ('pubis', 'pubis'), ('radioulna', 'radioulna'), ('radius', 'radius'), ('rib', 'rib'), ('sacrum', 'sacrum'), ('scaphoid', 'scaphoid'), ('scapholunar', 'scapholunar'), ('scapula', 'scapula'), ('scute', 'scute'), ('sesamoid', 'sesamoid'), ('shell', 'shell'), ('skeleton', 'skeleton'), ('skull', 'skull'), ('sphenoid', 'sphenoid'), ('sternum', 'sternum'), ('talon', 'talon'), ('talus', 'talus'), ('tarsal (indet.)', 'tarsal (indet.)'), ('tarsometatarsus', 'tarsometatarsus'), ('tarsus', 'tarsus'), ('temporal', 'temporal'), ('tibia', 'tibia'), ('tibiotarsus', 'tibiotarsus'), ('tooth (indet.)', 'tooth (indet.)'), ('trapezium', 'trapezium'), ('trapezoid', 'trapezoid'), ('triquetrum', 'triquetrum'), ('ulna', 'ulna'), ('vertebra', 'vertebra'), ('vomer', 'vomer'), ('zygomatic', 'zygomatic'), ('pharyngeal teeth', 'pharyngeal teeth'), ('molars', 'molars'), ('tusk', 'tusk'), ('horn corn', 'horn corn'), ('spine', 'spine'), ('silicified wood', 'silicified wood'), ('dentary', 'dentary'), ('cleithrum', 'cleithrum'), ('skull plate', 'skull plate'), ('basicranium', 'basicranium'), ('angulararticular', 'angulararticular'), ('ribs', 'ribs'), ('lateral ethmoid', 'lateral ethmoid'), ('pterotic', 'pterotic'), ('tooth roots', 'tooth roots'), ('shells', 'shells'), ('pharyngeal tooth', 'pharyngeal tooth'), ('ilium', 'ilium'), ('hemimandible', 'hemimandible'), ('pectoral spine', 'pectoral spine'), ('palate', 'palate'), ('pelvis', 'pelvis'), ('long bone', 'long bone'), ('axis', 'axis'), ('acetabulum', 'acetabulum'), ('magnum', 'magnum'), ('hemi-mandible', 'hemi-mandible'), ('weberian', 'weberian'), ('supraoccipital', 'supraoccipital'), ('anguloarticular', 'anguloarticular')], max_length=50, null=True, verbose_name='Element'),
        ),
        migrations.AlterField(
            model_name='biology',
            name='element_modifier',
            field=models.CharField(blank=True, choices=[('articulated', 'articulated'), ('caudal', 'caudal'), ('cervical', 'cervical'), ('coccygeal', 'coccygeal'), ('distal', 'distal'), ('intermediate', 'intermediate'), ('lower', 'lower'), ('lumbar', 'lumbar'), ('manual', 'manual'), ('manual distal', 'manual distal'), ('manual intermediate', 'manual intermediate'), ('manual proximal', 'manual proximal'), ('medial', 'medial'), ('pedal', 'pedal'), ('pedal distal', 'pedal distal'), ('pedal intermediate', 'pedal intermediate'), ('pedal proximal', 'pedal proximal'), ('proximal', 'proximal'), ('sacral', 'sacral'), ('thoracic', 'thoracic'), ('upper', 'upper'), ('indeterminate', 'indeterminate')], max_length=50, null=True, verbose_name='Element Mod'),
        ),
        migrations.AlterField(
            model_name='biology',
            name='identified_by',
            field=models.CharField(blank=True, choices=[('Z. Alemseged', 'Z. Alemseged'), ('R.L. Bernor', 'R.L. Bernor'), ('R. Bobe-Quinteros', 'R. Bobe-Quinteros'), ('P. Brodkorb', 'P. Brodkorb'), ('H.B.S. Cooke', 'H.B.S. Cooke'), ('E. Delson', 'E. Delson'), ('C. Denys', 'C. Denys'), ('G.G. Eck', 'G.G. Eck'), ('V. Eisenmann', 'V. Eisenmann'), ('N. Fessaha', 'N. Fessaha'), ('L.J. Flynn', 'L.J. Flynn'), ('S.R. Frost', 'S.R. Frost'), ('A.W. Gentry', 'A.W. Gentry'), ('D. Geraads', 'D. Geraads'), ('R. Geze', 'R. Geze'), ('F.C. Howell', 'F.C. Howell'), ('Institute Staff', 'Institute Staff'), ('D.C. Johanson', 'D.C. Johanson'), ('W.H. Kimbel', 'W.H. Kimbel'), ('H.B. Krentza', 'H.B. Krentza'), ('B.M. Latimer', 'B.M. Latimer'), ('M.E. Lewis', 'M.E. Lewis'), ('C.A. Lockwood', 'C.A. Lockwood'), ('T.K. Nalley', 'T.K. Nalley'), ('G. Petter', 'G. Petter'), ('J.C. Rage', 'J.C. Rage'), ('D. Reed', 'D. Reed'), ('K.E. Reed', 'K.E. Reed'), ('J. Rowan', 'J. Rowan'), ('M. Sabatier', 'M. Sabatier'), ('B.J. Schoville', 'B.J. Schoville'), ('A.E. Shapiro', 'A.E. Shapiro'), ('G. Suwa', 'G. Suwa'), ('E.S. Vrba', 'E.S. Vrba'), ('L.A. Werdelin', 'L.A. Werdelin'), ('H.B. Wesselman', 'H.B. Wesselman'), ('T.D. White', 'T.D. White')], max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='biology',
            name='life_stage',
            field=models.CharField(blank=True, choices=[('infant', 'infant'), ('juvenile', 'juvenile')], max_length=50, null=True, verbose_name='Life Stage'),
        ),
        migrations.AlterField(
            model_name='biology',
            name='sex',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Sex'),
        ),
        migrations.AlterField(
            model_name='biology',
            name='side',
            field=models.CharField(blank=True, choices=[('L', 'L'), ('R', 'R'), ('Indeterminate', 'Indeterminate'), ('L+R', 'L+R')], max_length=50, null=True, verbose_name='Side'),
        ),
    ]
#!/usr/bin/python

import sys
import re
import csv
import traceback

import datetime

from plan.plan import * 
from demat.demat import * 
from isin.isin import * 

class Tbd(Isin, Plan, Demat):
	def __init__(self):
		super(Tbd, self).__init__()
		# Plan.__init__(debug_level)
		# Demat.__init__(debug_level)
	
	def set_debug_level(self, debug_level):
		self.debug_level = debug_level

	def load_tbd_data(self, isin_bse_filename, isin_nse_filename, plan_filename, demat_filename):
		self.load_isin_bse_data(isin_bse_filename)
		self.load_isin_nse_data(isin_nse_filename)
		self.load_demat_data(demat_filename)
		self.load_plan_data(plan_filename)

	def print_tbd_phase1(self, out_filename, plan_only = None, tbd_only = None, days_filter = None):
		fh = open(out_filename, "w")
		fh.write('comp_name, plan_units_1k, demat_units_1k, tbd_units, tbd_pct, demat_last_txn_date, demat_last_txn_type, top_500\n')
		for comp_name in sorted(self.plan_comp_units):
			try:
				plan_units = int(self.plan_comp_units[comp_name])

				if plan_only and plan_units <= 0:
					if self.debug_level > 1:
						print 'no planned units : ', comp_name
					continue	

				isin_code = self.get_isin_code_by_name(comp_name)

				if isin_code == '':
					top_500 = 'NO'
					if self.debug_level > 1:
						print 'not in nse 500 ', comp_name
				else:
					top_500 = 'yes'

				demat_units = int(self.get_demat_units_by_isin_code(isin_code)) 
				demat_last_txn_date = self.get_demat_last_txn_date_by_isin_code(isin_code)
				if demat_last_txn_date != '':
					last_datetime = datetime.datetime.strptime(demat_last_txn_date, '%d-%b-%Y').date()
					my_delta = datetime.datetime.now().date() - last_datetime
					last_txn_days = my_delta.days
				else:
					last_txn_days = 0

				demat_last_txn_type = self.get_demat_last_txn_type_by_isin_code(isin_code)
				tbd_units = plan_units - demat_units
				if plan_units <= 0:
					tbd_pct = 0
				else:
					tbd_pct = float((100.0*tbd_units)/plan_units)
				tbd_pct = format(tbd_pct, '.2f')
				p_str = comp_name
				p_str += ',' 
				p_str += str(plan_units)
				p_str += ',' 
				p_str += str(demat_units)
				p_str += ',' 
				p_str += str(tbd_units) 
				p_str += ',' 
				p_str += str(tbd_pct) 
				p_str += ',' 
				p_str += demat_last_txn_date 
				p_str += ',' 
				p_str += demat_last_txn_type
				p_str += ',' 
				p_str += top_500 
				p_str += '\n' 
				if tbd_only:
					if tbd_units > 0:
						if days_filter:
							if last_txn_days > days_filter :
								fh.write(p_str)
						else:	
							fh.write(p_str)
				else:
					fh.write(p_str)
			except ValueError:
				print 'except : ValueError :', comp_name
		fh.close()

	def print_tbd_phase2(self, out_filename):
		self.print_tbd_phase1(out_filename, True)

	def print_tbd_phase3(self, out_filename):
		self.print_tbd_phase1(out_filename, True, True)

	def print_tbd_phase4(self, out_filename, days_filter):
		self.print_tbd_phase1(out_filename, True, True, days_filter)

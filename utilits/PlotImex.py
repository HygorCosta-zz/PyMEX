# -*- coding: utf8 -*-
"""
# Copyright (c) 2019 Hygor Costa
#
# This file is part of Py_IMEX.
#
#
# You should have received a copy of the GNU General Public License
# along with HUM.  If not, see <http://www.gnu.org/licenses/>.
#
# Created: Jul 2019
# Author: Hygor Costa
"""
import matplotlib.pyplot as plt


class PlotImex:

    def __init__(self, report_resul):
        self.time = report_resul[0]
        self.production = report_resul[1]
        self.wells_rate = report_resul[2]
        self.average_pressure = report_resul[3]

    def plot_cum_oil(self):
        plt.figure()
        prod_oil = self.production[:, 0]
        plt.plot(self.time, prod_oil, 'r')
        plt.xlabel('Time [days]')
        plt.ylabel('Cumulative oil production [m3]')
        plt.title('Cumulative production')
        plt.grid()
        plt.show()

    def plot_cum_water(self):
        plt.figure()
        prod_water_prod = self.production[:, 1]
        plt.plot(self.time, prod_water_prod, 'b')
        plt.xlabel('Time [days]')
        plt.ylabel('Cumulative water production [m3]')
        plt.title('Cumulative production')
        plt.grid()
        plt.show()

    def plot_cum_gas(self):
        plt.figure()
        prod_gas_prod = self.production[:, 2]
        plt.plot(self.time, prod_gas_prod, 'g')
        plt.xlabel('Time [days]')
        plt.ylabel('Cumulative water production [m3]')
        plt.title('Cumulative production')
        plt.grid()
        plt.show()

    def plot_cumulative_production(self):
        plt.figure()
        prod_oil = self.production[:, 0]
        prod_water_prod = self.production[:, 1]
        plt.plot(self.time, prod_oil, 'r', label='Cumulative Oil')
        plt.plot(self.time, prod_water_prod, 'b', label='Cumulative Walter')
        plt.legend(loc="upper left")
        plt.xlabel('Time [days]')
        plt.ylabel('Cumulative oil and water production [m3]')
        plt.title('Cumulative production')
        plt.grid()
        plt.show()

    def plot_average_pressure(self):
        plt.figure()
        plt.plot(self.time, self.average_pressure, 'g')
        plt.xlabel('Time [days]')
        plt.ylabel('Average Pressure [kg/cm2]')
        plt.title('Average Pressure of the Reservoir')
        plt.grid()
        plt.show()

    def plot_oil_rate(self):
        plt.figure()
        oil_rate = self.wells_rate[:, 0]
        plt.plot(self.time, oil_rate, 'r')
        plt.xlabel('Time [days]')
        plt.ylabel('Oil rate production [m3/day]')
        plt.title('Rate production')
        plt.grid()
        plt.show()

    def plot_water_rate(self):
        plt.figure()
        water_rate = self.wells_rate[:, 1]
        plt.plot(self.time, water_rate, 'b')
        plt.xlabel('Time [days]')
        plt.ylabel('Water rate production [m3/day]')
        plt.title('Rate production')
        plt.grid()
        plt.show()

    def plot_liquid_rate(self):
        plt.figure()
        liquid_rate_pro = self.wells_rate[:, 2]
        liquid_rate_inj = self.wells_rate[:, 3]
        plt.plot(self.time, liquid_rate_pro, 'r',
                 label='Liquid Rate FIELD-PRO')
        plt.plot(self.time, liquid_rate_inj, 'b',
                 label='Liquid Rate FIELD-INJ')
        plt.xlabel('Time [days]')
        plt.ylabel('Liquid rate [m3/day]')
        plt.title('Liquid Rate Field')
        plt.grid()
        plt.show()

    def plot_rates(self):
        plt.figure()
        oil_rate = self.wells_rate[:, 0]
        plt.plot(self.time, oil_rate, 'r', label='Oil Rate')
        water_rate = self.wells_rate[:, 1]
        plt.plot(self.time, water_rate, 'b', label='Water Rate')
        liquid_rate = self.wells_rate[:, 2]
        plt.plot(self.time, liquid_rate, 'k', label='Liquid Rate')
        plt.legend()
        plt.xlabel('Time [days]')
        plt.ylabel('Rate production [m3/day]')
        plt.title('Rate production')
        plt.grid()
        plt.show()

    def plot_all(self):
        plt.figure(1)
        prod_oil = self.production[:, 0]
        prod_water_prod = self.production[:, 1]
        prod_gas_prod = self.production[:, 2]
        plt.plot(self.time, prod_oil, 'r', label='Cumulative Oil')
        plt.plot(self.time, prod_water_prod, 'b', label='Cumulative Walter')
        plt.plot(self.time, prod_gas_prod, 'g', label='Cumulative Gas')
        plt.legend(loc="upper left")
        plt.xlabel('Time [days]')
        plt.ylabel('Cumulative oil and water production [m3]')
        plt.title('Cumulative production')
        plt.grid()

        plt.figure(2)
        plt.plot(self.time, self.average_pressure, 'g')
        plt.xlabel('Time [days]')
        plt.ylabel('Average Pressure [kg/cm2]')
        plt.title('Average Pressure of the Reservoir')
        plt.grid()

        plt.figure(3)
        oil_rate = self.wells_rate[:, 0]
        plt.plot(self.time, oil_rate, 'r', label='Oil Rate')
        water_rate = self.wells_rate[:, 1]
        plt.plot(self.time, water_rate, 'b', label='Water Rate')
        liquid_rate = self.wells_rate[:, 2]
        plt.plot(self.time, liquid_rate, 'k', label='Liquid Rate')
        plt.legend()
        plt.xlabel('Time [days]')
        plt.ylabel('Rate production [m3/day]')
        plt.title('Rate production')
        plt.grid()

        plt.show()


from sympy import *
from sympy.functions import cos
import scipy
import math
import os
import platform
import subprocess
from pylatex import Document, Section, Subsection, Tabular, Math, TikZ, Axis, \
    Plot, Figure, Matrix, Alignat, MultiRow, MultiColumn
from pylatex.utils import italic, NoEscape, bold
import cmath
import sys
sys.path.insert(0,r'C:\Users\tduffett\PycharmProjects\Concrete')
import Clauses

class Column:
    def __init__(self,Shape,D,Width,Height,Reinforcement,fc,fsy,Cover):
        self.Shape = Shape
        self.D = D
        self.Width = Width
        self.Height = Height
        if Shape == 'Circular':
            no_bars,bar_dia = Reinforcement.split('N')
            self.Reinforcement = int(no_bars)*sympify(bar_dia)**2/4*pi
            self.no_bars = int(no_bars)
            self.bar_dia = sympify(bar_dia)
        else:
            no_bars_Asc,bar_dia_Asc = Reinforcement['Asc'].split('N')
            no_bars_Ast, bar_dia_Ast = Reinforcement['Ast'].split('N')
            self.Reinforcement_Asc = int(no_bars_Asc) * sympify(bar_dia_Asc) ** 2 / 4 * pi
            self.no_bars_Asc = int(no_bars_Asc)
            self.bar_dia_Asc = sympify(bar_dia_Asc)
            self.Reinforcement_Ast = int(no_bars_Ast) * sympify(bar_dia_Ast) ** 2 / 4 * pi
            self.no_bars_Ast = int(no_bars_Ast)
            self.bar_dia_Ast = sympify(bar_dia_Ast)
        self.fc = fc
        self.Nuo = 0
        self.E = 200000 #MPa
        self.Cover = Cover
        if Shape == 'Circular':
            self.Ag = D**2/4 * pi
        else:
            self.Ag =Width * Height
        self.fsy = 500
        i = Symbol('i')
        y = (self.D/2 - self.Cover) * cos(2 * pi / self.no_bars * i)
        k = max(y.subs(i, j) for j in range(self.no_bars))
        for j in range(self.no_bars):
            if y.subs(i,j) == k:
                self.bottom_bar = j
        self.dpc = 0


    def Squash_point(self, **kwargs):
        alpha_1 = 1 - 0.003*self.fc
        Nuo = alpha_1*self.fc*self.Ag + self.Reinforcement*self.fsy
        setattr(self,'Nuo',Nuo)
        setattr(self,'alpha_1',alpha_1)
        return N(Nuo/1000)



    def Decompression_point(self,**kwargs):
        gamma = max(0.97 - 0.0025*self.fc,0.67)
        alpha_1 = 1 - 0.003 * self.fc
        alpha_2 = max(0.85 - 0.0015*self.fc,0.67)
        if self.Shape == 'Circular':
            i = Symbol('i')
            r = self.D/2 - self.Cover  #alpha represents worst case reinforcement placement around center of column
            y = r*cos(2*pi/self.no_bars*i)

            dn = self.D/2 + y.subs(i,self.bottom_bar)

            r1 = self.D / 2
            Theta = 2*acos((r1 - dn) / r1)
            Area = pi * r1 ** 2 * Theta / (2 * pi) - r1 ** 2 / 2 * sin(Theta)
            CC = gamma*alpha_2*self.fc*Area
            x = 0
            Cs = 0
            ecs = 0
            ds = 0
            Cs1 = 0
            Asc = self.bar_dia ** 2 / 4 * pi
            for j in range(self.no_bars):
                x= min(0.003*(self.D/2 + y.subs(i,j) + dn)/dn,self.fsy/self.E)*self.E*Asc
                if x >=0:
                    Cs1 = Cs1 + x
                else:
                    pass
                Cs = N(Cs + min(0.003*(self.D/2 + y.subs(i,j) + dn)/dn,self.fsy/self.E)*self.E*Asc)
                ecs = ecs + Asc*self.fsy*(self.D/2 + y.subs(i,j))
                ds = ds + dn - (self.D/2 + y.subs(i,j))

            ds = ds/(self.no_bars)
            self.Squash_point()
            dpc = (alpha_1*self.Ag*self.fc*self.D/2 + ecs)/self.Nuo
            setattr(self,'dpc',dpc)
            x1 = N(dpc)
            #Cs = esc*self.E*Asc

            Mu = CC * (dpc - 0.5*gamma*dn) + Cs*(dpc - ds)
            return N(Cs/1000),N(x/1000), N(CC + Cs1)/1000, N(Mu)/1000**2
        else:
            pass


    def Balanaced_Point(self):
        gamma = max(0.97 - 0.0025 * self.fc, 0.67)
        alpha_1 = 1 - 0.003 * self.fc
        alpha_2 = max(0.85 - 0.0015 * self.fc, 0.67)
        self.Decompression_point()
        r = self.D / 2 - self.Cover
        i = Symbol('i')
        y = r * cos(2 * pi / self.no_bars * i)
        dn = 0.545*(self.D/2 + y.subs(i,self.bottom_bar))
        r1 = self.D / 2
        Theta = 2*acos((r1 - dn) / r1)
        Area = pi * r1 ** 2 * Theta / (2 * pi) - r1 ** 2 / 2 * sin(Theta)
        Cc = gamma*alpha_2*self.fc*Area
        Cs = 0
        ecs = 0
        ds = 0
        Cs1 = 0
        Asc = self.bar_dia ** 2 / 4 * pi
        for j in range(self.no_bars):
            po = N(max(min(0.003 * (dn - (self.D / 2 + y.subs(i, j))) / dn, self.fsy / self.E),-self.fsy/self.E) * self.E * Asc)
            Cs = N(Cs + max(min(0.003 * (dn - (self.D / 2 + y.subs(i, j))) / dn, self.fsy / self.E),-self.fsy/self.E) * self.E * Asc)
            ecs = ecs + Asc * self.fsy * (self.D / 2 - y.subs(i, j))
            ds = self.dpc - (self.D/2 + y.subs(i,j))
            Cs1 = Cs1 + max(min(0.003 * (dn - (self.D / 2 + y.subs(i, j))) / dn, self.fsy / self.E),-self.fsy/self.E) * self.E * Asc *(ds)
        ds = ds / self.no_bars
        self.Squash_point()
        dpc = (alpha_1*self.Ag * self.fc * self.D / 2 + ecs) / self.Nuo
        x1 = N(dpc)
        Nu = Cs + Cc
        Mu = Cc*(dpc-0.5*gamma*dn) + Cs1
        return N(Nu)/1000, N(Mu)/1000**2

    def Pure_Bending(self):
        gamma = max(0.97 - 0.0025 * self.fc, 0.67)
        alpha_1 = 1 - 0.003 * self.fc
        alpha_2 = max(0.85 - 0.0015 * self.fc, 0.67)
        self.Decompression_point()
        r = self.D / 2 - self.Cover
        i = Symbol('i')
        ku = Symbol('ku')
        y = r * cos(2 * pi / self.no_bars * i)
        dn = ku*(self.D/2 + y.subs(i,self.bottom_bar))
        r1 = self.D / 2
        Theta = 2*acos((r1-dn)/r1)
        Area = pi*r1**2*Theta/(2*pi) - r1**2/2*sin(Theta)
        Cc = alpha_2*self.fc*Area
        Cs = 0
        ecs = 0
        ds = 0
        Asc = self.bar_dia ** 2 / 4 * pi
        n = Symbol('n')
        #Cs = Sum(Max(Min(0.003 * (-self.D / 2 + y.subs(i, n) + dn) / dn, self.fsy / self.E),
                   #  -self.fsy / self.E) * self.E * Asc,(n,0,self.no_bars))
        for j in range(self.no_bars):
            #Cs = Cs + Piecewise((0.003 * (-self.D / 2 + y.subs(i, j) + dn) / dn,(0.003 * (-self.D / 2 + y.subs(i, j) + dn) / dn) <=(self.fsy / self.E)), (self.fsy / self.E,(0.003 * (-self.D / 2 + y.subs(i, j) + dn) / dn) >(self.fsy / self.E)))

            Cs = Cs + Max(Min(0.003 * (self.D / 2 - y.subs(i, j) - dn) / dn, self.fsy / self.E),
                         -self.fsy / self.E) * self.E * Asc

        for j in range(self.no_bars):

            ecs = ecs + Asc * self.fsy * (self.D / 2 - y.subs(i, j))
            ds = ds + (self.D / 2 - y.subs(i, j))
        ds = ds / self.no_bars
        self.Squash_point()
        dpc = (self.Ag * self.fc * self.D / 2 + ecs) / self.Nuo
        Nu = Cs - Cc
        x =0.41
        x1 = N(Cc.subs(ku,x))
        x2 = N(Cs.subs(ku,x))
        x3 = N(Nu.subs(ku,x))

        #ku1 = scipy.fsolve(Nu,0.1)
        ku1 = nsolve(Nu,0.1)
        Mu = Cc*(dpc-0.5*gamma*dn) + Cc*(dpc - ds)
        Mu = Mu.subs(ku,ku1)
        Nu = Nu.subs(ku,ku1)
        return ku1,N(Nu)/1000, N(Mu)/1000**2

def printout(self):
    standard = ' AS3600:2018 '
    geometry_options = {'tmargin': '1cm', 'lmargin': '1cm'}
    doc = Document('Document_name', geometry_options=geometry_options)
    with doc.create(Section('Design of Concrete Column', numbering=False)):
        Clauses.Cl10622(doc)
    with doc.create(Subsection(NoEscape('Calculation of Squash Load N_{uo}'),numbering=False)):
        doc.append(NoEscape('$N_{uo} = \\alpha_{1} f\'_{c} A_{g} + A_{s} f_{sy}$'))
        doc.append('\n\n')
        doc.append(NoEscape(r'$\alpha_{1} = ' + str(self.alpha_1)+'$'))
        doc.append('\n\n')
        if self.Shape =='Circular':
            doc.append('The section is circular, therefore:')
            doc.append('\n')
            doc.append(NoEscape('$Ag = \pi r^{2}$'))
            doc.append('\n\n')
            doc.append(NoEscape('$A_{st} = $' + str(N(self.Reinforcement,5)) + '$mm^{2}$'))
            doc.append('\n\n')
        else:
            doc.append('The section is circular, therefore:')
            doc.append('\n')
            doc.append(NoEscape('$Ag = width x depth$'))
            doc.append('\n\n')
            doc.append(NoEscape('$A_{st} = $' + str(N(self.Reinforcement_Asc + self.Reinforcement_Ast, 5)) + '$mm^{2}$'))
            doc.append('\n\n')
        doc.append(NoEscape('$Ag = ' + str(N(self.Ag,5)) +'$ $ mm^{2}$'))
        doc.append('\n\n')

        doc.append(NoEscape('$N_{uo} = ' + str(N(self.Nuo/1000,5)) +' $ kN'))
        doc.append('\n\n')


    with doc.create(Subsection('Decompression Point',numbering=False)):
        Clauses.Cl10623(doc)
    with doc.create(Subsection('Calculation of Decompression Point',numbering=False)):
        doc.append('Hello')
    doc.generate_tex()
    subprocess.run(['pdflatex', '-interaction=nonstopmode', 'Document_name.tex'])


Shape = 'Circular'
D = 300
Width = 0
Height = 0
Reinforcement = '6N20' #If circular, type reinforcing bars in format {No.bars}N{bar Dia}
fc = 25
fsy = 400
Cover = 40


C = Column(Shape,D,Width,Height,Reinforcement,fc,fsy,Cover)
print('Squash Point' ,C.Squash_point())
print('Squash Point' ,C.Nuo)
print('Decompression Point' ,C.Decompression_point())
print('Balanced Point' ,C.Balanaced_Point())
print('Pure Bending' ,C.Pure_Bending())
#printout(C)

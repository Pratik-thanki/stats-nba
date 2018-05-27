from sqlalchemy import create_engine
from Links import *
import pandas as pd
import seaborn as sns; sns.set(style="ticks", color_codes=True)
import matplotlib.pyplot as plt


# engine = create_engine('mssql+pyodbc://' + ms_sql)
engine = create_engine('mysql+mysqlconnector://' + str(my_sql))
cursor = engine.connect()
gamePlays = pd.read_sql("SELECT ClockTime, Description, EType, Evt, GameID, LocationX, LocationY, MType, Period, PlayerID, TeamID FROM GamePlays", engine)


shotsMade = gamePlays.loc[(gamePlays['EType'] == 1) & (gamePlays['GameID'] == 11500018)]
shotsMissed = gamePlays.loc[(gamePlays['EType'] == 2) & (gamePlays['GameID'] == 11500018)]
shotsAll = gamePlays.loc[((gamePlays['EType'] == 1) | (gamePlays['EType'] == 2)) & (gamePlays['GameID'] == 11500018)]


# scatter plot with distribution on axis
g = sns.JointGrid(x="LocationX", y="LocationY", data=shotsAll).plot_joint(plt.scatter, color=".5", edgecolor="white").plot_marginals(sns.distplot, kde=False, color=".5")


# hex plot
g = (sns.jointplot(x="LocationX", y="LocationY", data=shotsAll, kind="hex", stat_func=None).set_axis_labels("x", "y"))
plt.show()



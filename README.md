# Project C: Exploratory Dashboard of Cost of Living and Living Wages
## Community Action Computing, Westmont College 
#### Prof. Mike Ryu *mryu@westmont.edu*
#### Author: Allie Peterson 


*** 

This project is part of my Community Action Computing class and focuses on creating an exploratory dashboard that gives 
users the opportunity to explore cost of living in the US over the last 50 years. 
***
### ExTRA CREDIT CHANGES
Based on the feedback I received, I changed my: 
- line graph to show more smooth lines. the issue was that the x-axis was plotting multiple months of data on single year 
x-values. To fix it, I changed the data I was using from "year" to "observation date"
- bar graph to always show accurate data. To fix it, I filtered my data and only kept values that had income data.
- slider values for gas increased to represent the average miles driven in a month.

### Example Discoveries from this Exploratory Dashboard
- The user realizes that they have more money at their disposal then they may have thought. 
- The user realizes that they have less money at their disposal then they may have thought. 
- The user realizes that although things feel more expensive, the income is increasing as well. 

### The Region 
As I read through this assignments [pre-reading article](https://livingwage.mit.edu/pages/methodology) on living wage and how it is estimated, 
I wondered its players have changed over time in the US. The US has a reputation of being quite rich, but I wanted to take a deeper dive into what that looks like for the average American. 


### The Data 
All of the data I'm using for this project is sourced from FRED, Federal Reserve Bank of St. Louis.
- [Median Household Income](https://fred.stlouisfed.org/series/MEHOINUSA672N)
  - This dataset has the median household income in the US over the last 50 years. I chose this dataset to show 
  how the median household income of my selected region has changed over time.
- [Median Cost of Houses Sold](https://fred.stlouisfed.org/series/MSPUS) 
  - This dataset has the cost of houses sold in the US over the last 50 years. I chose this dataset to show 
    how the costs of certain capital expenses for a typical household in my selected region have changed over time.
- [Median Cost of Chicken](https://fred.stlouisfed.org/series/APU0000706111)
  - This dataset has the median cost of chicken in the US over the last 50 years. I chose this dataset to show 
    how the costs of household goods in my selected region have changed over time.

- [Average Cost of Gas](https://fred.stlouisfed.org/series/GASREGCOVW)
  - This dataset has average cost of gas in the US over the last 30 years. Because most individuals commute in some way, I chose this dataset to show
    how another factor impacts the finances of the typical household, and how it has changed over time.


### SwD Strategies 
- **Color**: I used color to create a heatmap, making variations in PM2.5 levels more visually intuitive. I considered making the button green but decided against it to avoid drawing attention away from the graph (p. 120).
- **Simple Text**: I kept text minimal in my slideshow, allowing the visuals to take center stage while leaving detailed explanations for my verbal presentation (p. 38).
 **Storyboarding**: Mapping out the flow of my story helped shape the structure of my visualization. This process led me to use a slider to display monthly trends (p. 31-33).
- **Big Idea**: I used this technique to develop a clear thesis and build my three-minute story around it (p. 31).

*** 
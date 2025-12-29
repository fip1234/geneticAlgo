####CHECK##plot.py
#functions to plot results from mountain_sim.py  

import matplotlib.pyplot as plt
import pandas as pd

def plot_fitness(generation_list, best_fitness_list, mean_fitness_list, 
                 filename='fitness_evolution.png', title='Fitness Evolution Over Generations '):
    plt.figure(figsize=(10, 6))
    #blue line with circles
    plt.plot(generation_list, best_fitness_list,'b-o',label='Best Fitness',linewidth=2)
    #red dashed line with squares 
    plt.plot(generation_list, mean_fitness_list,'r--s',label='Mean Fitness',linewidth=2)
    plt.xlabel('Generation', fontsize=12)
    plt.ylabel('Height Reached', fontsize=12)
    plt.title(title, fontsize=14)
    plt.legend(fontsize=10)
    plt.grid(True, alpha=0.3)
    #high res
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.show()
    print("Graph saved as", filename)
    plt.close()

#convert results to dataframe and save as CSV
def save_table(generation_list, best_fitness_list, mean_fitness_list, filename='results.csv'):
    data = {
        'Generation':generation_list,
        'Best_Height':best_fitness_list,
        'Mean_Height':mean_fitness_list
    }
    #dict to df table
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)
    print("results saved as", filename)
    print("first 10 rows:")
    print(df.head(10))
    return df


#end
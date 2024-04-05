#Working plan for this: 

# use sample data from the original sample_data file: 

from sample_data import preprocessing, data_pull
from chat_gpt import ranking_server
import sys
sys.path.insert(0, '/sample_data/data_pull.py')

#need to run python preprocessing.py before this, but not sure how 
data = data_pull.data_puller('TWITTER', 10000, 1, "username")

sys.path.insert(0, '/examples/chat_gpt/ranking_server.py')

chat_gpt_rankings = ranking_server.generate_rankings(data)

# use the chat_gpt model results to train the mistral model 
# the way I'm doing this right now doesn't feel intuitive--maybe something else here? 
#current strategy is 



# fine tune the model 

# call upon the model to rank new posts 
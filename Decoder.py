import pandas as pd
import os
"""
    This is the module for converting files to the correct json format
    the functions here must take two path, input file and output file
    the output will always be json and must be in the format:
    Submission Date: YYYY-MM-DD HH:MM:SS
    Email: String
    Preference: String with the name of the film
    Position: Int rank of film
    Points: Float rank of film normalized between 1 and 0 (1 if in first position 0 if last
"""

def analyze_jot(input_path, output_path=None, preference=None):
    """
    decodes csv from the horrible jotform format
    :param input_path: string path of the file
    :param output_path: string path of new file in json format, if None left
    the name of the input is used
    :param preference: string name in the header of the column that contains the vote
    :return: graph object
    """
    if output_path is None:
        output_path = os.path.splitext(input_path)[0]+'.json'
    if preference is None:
        preference = 'Ordina i film in base alle tue preferenze'

    data = pd.read_csv(input_path)
    data = data.rename(columns={preference: 'Preference'})
    data['Preference'] = data['Preference'].map(lambda s: s.split('\r\n'))
    data = data.explode(column='Preference')
    data['Position'] = data['Preference'].map(lambda s: s.split(':')[0]).astype('int64')
    data['Preference'] = data['Preference'].map(lambda s: s.split(': ')[1])
    m = data['Position'].max()
    data['Points'] = data['Position'].map(lambda n: (m-n)/(m-1))
    data = data.reset_index().drop(columns='index')
    data.to_json(output_path)
    return

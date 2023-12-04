import penman
from pathlib import Path
from conllu import parse
from penman.graph import Graph
from penman.codec import PENMANCodec
from conllu import parse_incr
from conllu import parse




def target_node(conll_gold, grammatical_function):
    '''
    get the head information according to the gold annotation
    :param conll_gold: gold conllu file
    :return: a list of tuples (the head id, the head token, and the grammatical function of the head)
    '''
    head_tokens =[]
    for i, conll in enumerate(conll_gold):
        tokens = [x for x in conll]
        heads =[]
        for token in conll:
            if token['deprel'] == 'acl:relcl': #find the relative clauses first
                head_id = int(token['head'])
                head_info = [x for x in tokens if x['id'] == head_id][0]
                head_xpos = head_info['xpos']
                if head_xpos not in ['WDT', 'WP', 'WRB']:
                    head_token = head_info['form']
                    head_rel =['obj']
                    if head_rel[0] in grammatical_function or ' '.join(grammatical_function) in head_rel[0]:
                        print(head_rel[0])
                        head = (head_id, head_token)
                        heads.append(head)
        head_tokens.append((heads, i))
    return head_tokens

def find_node(alignment, head_id):
    '''
    to find the node that represents the head token
    :param alignment: the alignment document
    :param head_id: the head_id returned from the target_node function
    :return:
    '''
    # assert len(alignment)==len(head_id)
    head_nodes =[]
    for i, alignment_element in enumerate(alignment):
        correct_sent = [x[1] for x in head_id]
        if i in correct_sent:
            sentence = alignment_element.split('nodealignment=')[0].strip().split('\n')
            node_token_alignment = alignment_element.split('nodealignment=')[1][1:-2].strip().split(', ')
            head_node = []
            token_id = [x.split('@@')[0] for x in node_token_alignment]
            token_node = [x.split('@@')[-1] for x in node_token_alignment]
            for j, token in enumerate(sentence):
                for h in head_id[i][0]:

                    if h[1] in token.split('\t')[1]:

                        head_id[i][0].remove(h)
                        nodes = [y for x, y in zip(token_id, token_node) if int(x)-1==j] #find the target node
                        for x in nodes:
                            head_node.append(x)

            head_nodes.append(head_node)
    return head_nodes

def find_reentrancies(pred_amr, head_nodes, head_id):
    reentrancies = []
    reentrancies_general = []
    codec = PENMANCodec()
    for i, x in enumerate(pred_amr):
        correct_sent = [x[1] for x in head_id]
        if i in correct_sent:
            drs_triple = codec.decode(x).triples
            label_node_pair = {x[0]:x[2].replace('\"', '') for x in drs_triple if x[1]==':instance'}
            to_node = [x[2] for x in drs_triple if x[1]!=':instance' and x[2].startswith('u_') ] #only works for amparser
            # to_node_name = [label_node_pair[x[2]] for x in drs_triple if x[1]!=':instance' and x[2].startswith('u_')]
            if len(to_node) != len(set(to_node)):
                reentrancies_general.append(drs_triple)
                reentrancy_node = list(set([label_node_pair[x] for x in to_node if to_node.count(x) > 1]))
                print(reentrancy_node) #the node that has renentrancies
                print(head_nodes[i]) # the real node that should have reentrancies
                overlap = [x for x in reentrancy_node if x in head_nodes[i]]
                if overlap:
                    reentrancies.append(drs_triple)

        reentrency_perc = round(len(reentrancies)/len(pred_amr),3)
        print(f'Num of amrs:\t{len(head_nodes)}\nnum of examples that receive reentrancies:\t{len(reentrancies_general)}\n'
              f'num of examples in which the head node receives reentrancies:\t {len(reentrancies)} ({reentrency_perc})')


if __name__== '__main__':
    pred_amr = Path('output_rc/pred_pc.txt').read_text().strip().split('\n\n')
    alignment = Path('output_rc/alignment_pc.txt').read_text().strip().split('sentence=')[1:]
    conll_gold = open('rc/pc.conllu', 'r')
    conll = [x for x in parse_incr(conll_gold)]
    head_id = target_node(conll, ['obj'])
    head_nodes = find_node(alignment, head_id)
    print(len(head_id))
    print(len(alignment))
    print(len(pred_amr))
    find_reentrancies(pred_amr, head_nodes, head_id)
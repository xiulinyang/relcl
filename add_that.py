def add_relative_pronoun(sents_reduced):
    wrong_annotation = []
    all_sents = []
    all_that_ids = []
    for sent in sents_reduced:
        raw_sent = []  # TODO: check if '-' influences the script.
        that_id = []
        num_reduced = 0  # how many reduced relatives in one sentence
        for i, token in enumerate(sent):
            try:
                if '-' not in str(token['id']):
                    raw_sent.append(token['form'])
                    if token['deprel'] == 'acl:relcl':
                        head_dep = [x for x in sent if x['id'] == token['head']][0]
                        head_deps = [x[1] for x in head_dep['deps'] if x[1] == token['id']]
                        if head_deps == [] and head_dep['xpos'] not in ['WDT', 'WP']:
                            that_position = [x['id'] for x in sent if x['id'] == token['head']][0]
                            raw_sent.insert(that_position + num_reduced, 'that')
                            that_id.append(that_position + num_reduced)
                            num_reduced += 1
                            assert str(raw_sent[that_position + num_reduced - 2]) == str(head_dep['form'])
            except AssertionError:
                print(raw_sent)
                wrong_annotation.append(sent.serialize())
                print(len(wrong_annotation))
                continue
        all_sents.append(raw_sent)
        all_that_ids.append(that_id)

    return all_sents, all_that_ids, wrong_annotation


def add_enhanced_rule(sents, that_ids, original_sents):
    with open('eud_others_r.conllu', 'w') as conllu:
        for i, sent in enumerate(sents):
            print(' '.join(sent))
            parsed_sent = nlp([sent]).sentences[0]
            for id in that_ids[i]:
                deprel = [token.deprel for token in parsed_sent.words if token.id==id[0]][0]
                head_index = [j for j, x in enumerate(original_sents[i]) if x['id']==id[1]][0]
                original_sents[i][head_index]['deps'].append((deprel, id[2]))
                print(id[1], deprel, id[2])
                print(original_sents[i])
            conllu.write(original_sents[i].serialize())
            conllu.write('\n')

add_enhanced_rule(gum_sent_with_that, gum_that_ids, sents_reduced)

gum_sent_with_that, gum_that_ids, gum_wrong_annotation = add_relative_pronoun(sents_reduced)
def __getAttributesFromMsg(self) -> list:
    attList = []
    synonyms = self.__AIE.getSynonyms(self.entity_class)

    # finding the index after the entity class name in the message
    entity_class_token_idx = -1
    for i, token_i in enumerate(self.tokens):
        # advance forward until the token of the entity class is found
        if token_i['word'] in synonyms:
            entity_class_token_idx = i
            break

    if entity_class_token_idx > -1:  # if the entity class token was found
        question_answerer = self.__AIE.getPipeline('question-answering')
        # iterate over the tokens and find the attribute names and values
        j = entity_class_token_idx + 1
        while j < len(self.tokens):
            # advance foward until the token of the type "NOUN" is found (i.e. the first noun it is an attribute name)
            token_j = None
            while j < len(self.tokens) and token_j is None:
                if self.tokens[j]['entity'] == 'NOUN':
                    token_j = self.tokens[j]
                else:
                    j += 1

            if token_j:
                # found the first noun after token_j. It is the attribute name
                attribute_name = token_j['word']
                # ask by the attribute value using question-answering pipeline
                response = question_answerer(question='What is the ' + attribute_name +
                                                      ' of the ' + self.entity_class + '?',
                                             context=self.user_msg)
                # save the pair of attribute name and attribute value in the result list
                attList.extend([attribute_name, response['answer']])
                # update the j index to the next token after the attribute value
                # get the end index in the original msg
                att_value_idx_end = self.user_msg.find(response['answer'])
                if att_value_idx_end > -1:
                    att_value_idx_end = att_value_idx_end + len(response['answer'])
                    while j < len(self.tokens) and self.tokens[j]['start'] < att_value_idx_end:
                        j += 1
            else:
                # no noun found after token_j. It is the end of the attribute list
                break

    return attList

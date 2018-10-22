from gensim.scripts.glove2word2vec import glove2word2vec
from gensim.models.keyedvectors import KeyedVectors


def main ():
	# glove2word2vec(glove_input_file="glove.6B.50d.txt", word2vec_output_file="glove.6B.50d_model.txt")
	glove_model = KeyedVectors.load_word2vec_format("glove.6b.50d_model.txt", binary=False)
	#findTopTenSynonyms(glove_model)

main()
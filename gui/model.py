import pysmile
import pysmile_license
nodes = ["age35", "cardiotoxicity", "chemo_adiu", "chemo_neo", "cohort", "cvds",
         "death_in_5y", "dyslipidemia", "grade", "histology", "hormons_adiu", "hormons_neo",
         "hypertension", "ischemic_heart_disease", "ki67", "pn", "pt", "radio_adiu",
         "radio_neo", "receptors", "surgery", "t2db", "target_adiu", "target_neo", "vascular"]
evidence = {node : "" for node in nodes}
#print(evidence)

def evaluateCardiovascularDiseaseIn5Years(evidence : dict) -> float:
    ## network creation and loading
    net = pysmile.Network()
    net.read_file("model_latest/extended_model.xdsl");
    ## set evidence
    if not(len(evidence) == 0):
        for key in evidence:
            if len(str(evidence[key])) != 0:
                if str(evidence[key]) != "nan":
                    #print(key + " : " + evidence[key])
                    net.set_evidence(key, evidence[key])
    ## updating network 
    net.update_beliefs()
    ## getting posterior probabilities 
    beliefs = net.get_node_value("cvds")
    ''''
    for i in range(0, len(beliefs)):
            print(net.get_outcome_id("cvds", i) + "=" + str(beliefs[i])) 
    '''
    ## returning result ([0]<- P(NO) [1]<-P(YES))
    return beliefs[1]

#print(evaluateCardiovascularDiseaseIn5Years(evidence))
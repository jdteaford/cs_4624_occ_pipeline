<template>
	<div class="main">
		<div class="subpage_box">
		<div class="dot_holder">
				<div class="dot1" @click="$router.push('/')"></div>
				<div class="dot2"></div>
				<div class="dot3"></div>
		</div>
		<div class="title">
		    <h2 id="titletrain">Perform Inference</h2>
		</div>
		<form class="main_form">
		    <div class="content-left">
			<div class="align-horizontal">
		    		<p class="label">Upload Inference Data</p>
		    		<p class="upload_type"><input type="file" ref="inferenceData" @change="updateInferenceData" multiple></p>
			</div>
			<div class="align-horizontal">
		    	<p class="label">Upload Inference Model</p>
		    	<p class="upload_type"><input type="file" ref="inferenceModel" @change="updateInferenceModel" multiple></p>
			</div>
			<div class="align-horizontal">
		    	<p class="label">Inference Model Type</p>
		    	<p class="upload_type"><select v-model="inference_model_type">
		    	        <option></option>
	    	        	<option value='svm'>One-class SVM</option>
	    	        	<option value='ae'>Autoencoder</option>
		    	</select></p>
			</div>
			<div class="align-horizontal">
		    	<p class="label">Inference Data Type</p>
		    	<p class="upload_type"><select v-model="inference_data_type">
		    	        <option></option>
		    	        <option value='urls'>Zipfile of URLs</option>
		    	        <option value='html'>Zipfile of HTML</option>
		    	        <option value='txt'>Zipfile of .txt files</option>
		    	</select></p>
			</div>
			<div class="align-horizontal">
			<p class="align-center"><button type="button" @click="inference">Perform Inference</button></p>
			</div>
		    </div>
		</form>
		<div v-if="show_tsne" class="loss_curve">
			<div class="document_holder">
				<div v-for="document in documents">
					<DocumentCard :threshold="threshold" :related="document" :lab="'Unknown'"/>
				</div>
			</div>
		</div>

		</div>
	</div>
</template>

<script>
import axios from 'axios';
import DocumentCard from './DocumentCard.vue'

export default {
  name: 'Ping',
  components: {
    DocumentCard
  },
  data() {
    return {
      inference_data: [],
      inference_data_type: '',
      inference_model: [],
      inference_model_type: '',
      graph_data: {
        datasets: [{
	  data: []
	}]
      },
      show_tsne: false,
      graph_options: {
        responsive: true,
	maintainAspectRatio: false
      },
      threshold: 85,
      document_names: [],
      options: {
        min: 0,
        max: 100,
        interval: 1,
      },
      similarities: [],
    };
  },
  methods: {
    inference() {
      	const path = 'http://localhost:8000/inference';
	let formData = new FormData();
	formData.append("model", this.inference_model[0]);
	formData.append("data", this.inference_data[0]);
	formData.append("model_type", this.inference_model_type);
	formData.append("data_type", this.inference_data_type);
	this.submitForm(path, formData);
    },
    updateInferenceData() {
	this.inference_data = this.$refs.inferenceData.files;
    },
    updateInferenceModel() {
	this.inference_model = this.$refs.inferenceModel.files;
    },
    submitForm(path, formData) {
	axios.post(path, formData, {
	  headers: {
	    "Content-Type": "multipart/form-data"
	  },
	})
        .then((res) => {
	    this.similarities = res.data[0];
	    this.document_names = res.data[1];
	    this.show_tsne = true;
        })
        .catch((error) => {
          console.error(error);
        });
    }
  },
  computed: {
    accuracy: function() {
      let tps = 0;
      let ts = this.similarities.slice(0, 5);
      for (let i = 0; i < ts.length; i++) {
          if (ts[i] * 100 > this.threshold) {
      	tps += 1;
          }
      }
      let fps = 0;
      let fs = this.similarities.slice(5, 10);
      for (let i = 0; i < fs.length; i++) {
          if (fs[i] * 100 < this.threshold) {
              fps += 1;
          }
      }
      return (tps + fps) / 10;
    },
    documents: function() {
	    const zip = (a, b) => a.map((k, i) => [k, b[i]]);
	    return zip(this.similarities, this.document_names);
    },
  }
};
</script>
<style src="@vueform/slider/themes/default.css"></style>

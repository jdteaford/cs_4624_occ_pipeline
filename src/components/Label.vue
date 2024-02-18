<template>
	<div class="main">
		<div class="subpage_box">
		<div class="dot_holder">
				<div class="dot1" @click="$router.push('/')"></div>
				<div class="dot2"></div>
				<div class="dot3"></div>
		</div>
		<div class="title">
		    <h2 id="titletrain">Perform Labeling</h2>
		</div>
		<form class="main_form">
		    <div class="content-left">
			<div class="align-horizontal">
		    		<p class="label">Upload Related Labeling Data</p>
		    		<p class="upload_type"><input type="file" ref="relatedLabelingData" @change="updateRelatedLabelingData" multiple></p>
			</div>
			<div class="align-horizontal">
		    		<p class="label">Upload Unrelated Labeling Data</p>
		    		<p class="upload_type"><input type="file" ref="unrelatedLabelingData" @change="updateUnrelatedLabelingData" multiple></p>
			</div>
			<div class="align-horizontal">
		    	<p class="label">Upload Model</p>
		    	<p class="upload_type"><input type="file" ref="inferenceModel" @change="updateModel" multiple></p>
			</div>
			<div class="align-horizontal">
		    	<p class="label">Model Type</p>
		    	<p class="upload_type"><select v-model="model_type">
		    	        <option></option>
	    	        	<option value='svm'>One-class SVM</option>
	    	        	<option value='ae'>Autoencoder</option>
		    	</select></p>
			</div>
			<div class="align-horizontal">
		    	<p class="label">Data Type</p>
		    	<p class="upload_type"><select v-model="data_type">
		    	        <option></option>
		    	        <option value='urls'>Zipfile of URLs</option>
		    	        <option value='html'>Zipfile of HTML</option>
		    	        <option value='txt'>Zipfile of .txt files</option>
		    	</select></p>
			</div>
			<div class="align-horizontal">
			<p class="align-center"><button type="button" @click="labeling">Perform Labeling</button></p>
			</div>
		    </div>
		</form>
		<div v-if="show_tsne" class="loss_curve">
			<div class="loss_curve_inner">
			<div v-if="show_tsne" class="slider_box">
				<div class="slider_inner">
					<h2>Similarity Threshold</h2>
				</div>
				<Slider v-model="threshold" v-bind="options"/>
				<div class="slider_inner">
					<h2 id="#accuracy">Accuracy: {{ this.accuracy}}</h2>
				</div>
			</div>
			<div class="tsne_plot">
	    			<Scatter :data="graph_data_processed" :options="graph_options" />
			</div>
			</div>
			<div class="document_holder">
				<div v-for="related in relateds">
					<DocumentCard :threshold="threshold" :related="related" :lab="'Related'"/>
				</div>
				<div v-for="unrelated in unrelateds">
					<DocumentCard :threshold="threshold" :related="unrelated" :lab="'Unrelated'"/>
				</div>
			</div>
		</div>

		</div>
	</div>
</template>

<script>
import axios from 'axios';
import {
  Chart as ChartJS,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Legend
} from 'chart.js'
import { Scatter } from 'vue-chartjs'
import Slider from '@vueform/slider'
import DocumentCard from './DocumentCard.vue'

export default {
  name: 'Ping',
  components: {
    Scatter,
    Slider,
    DocumentCard
  },
  data() {
    return {
      data: [],
      data_type: '',
      model: [],
      model_type: '',
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
      threshold: 50,
      related_document_names: [],
      unrelated_document_names: [],
      options: {
        min: 0,
        max: 100,
        interval: 1,
      },
      unrelatedSimilarities: [],
      relatedSimilarities: [],
    };
  },
  methods: {
    labeling() {
      	const path = 'http://localhost:8000/labeling';
	let formData = new FormData();
	formData.append("model", this.model[0]);
	formData.append("unrelated_data", this.unrelatedLabelingData[0]);
	formData.append("related_data", this.relatedLabelingData[0]);
	formData.append("model_type", this.model_type);
	formData.append("data_type", this.data_type);
	this.submitForm(path, formData);
    },
    updateUnrelatedLabelingData() {
	this.unrelatedLabelingData = this.$refs.unrelatedLabelingData.files;
    },
    updateRelatedLabelingData() {
	this.relatedLabelingData = this.$refs.relatedLabelingData.files;
    },
    updateModel() {
	this.model = this.$refs.inferenceModel.files;
    },
    submitForm(path, formData) {
	axios.post(path, formData, {
	  headers: {
	    "Content-Type": "multipart/form-data"
	  },
	})
        .then((res) => {
	    this.relatedSimilarities = res.data[0];
	    this.unrelatedSimilarities = res.data[1];
	    this.graph_data = res.data[2]
	    this.related_document_names = res.data[3];
	    this.unrelated_document_names = res.data[4];
		let max_acc = 0;
		let max_i = 0;
		for (let i = 0; i < 100; i++) {
			this.threshold = i;
			if (this.accuracy > max_acc) {
				max_acc = this.accuracy;
				max_i = i;
			}
		}
		this.threshold = max_i;
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
      for (let i = 0; i < this.unrelatedSimilarities.length; i++) {
          if (this.unrelatedSimilarities[i] * 100 < this.threshold) {
	      tps += 1;
          }
      }
      let fps = 0;
      for (let i = 0; i < this.relatedSimilarities.length; i++) {
          if (this.relatedSimilarities[i] * 100 > this.threshold) {
              fps += 1;
          }
      }
      return (tps + fps) / 10;
    },
    relateds: function() {
	    const zip = (a, b) => a.map((k, i) => [k, b[i]]);
	    return zip(this.relatedSimilarities, this.related_document_names);
    },
    unrelateds: function() {
	    const zip = (a, b) => a.map((k, i) => [k, b[i]]);
	    return zip(this.unrelatedSimilarities, this.unrelated_document_names);
    },
    graph_data_processed: function() {
      let related = [];
      let unrelated = [];
      for (let i = 0; i < this.unrelatedSimilarities.length; i++) {
	      if (this.unrelatedSimilarities[i] * 100 < this.threshold) {
		      unrelated.push(this.graph_data[i]);
              }
	      else {
		      related.push(this.graph_data[i]);
	      }
      }
      for (let i = 0; i < this.relatedSimilarities.length; i++) {
	      if (this.relatedSimilarities[i] * 100 < this.threshold) {
		      unrelated.push(this.graph_data[i + this.unrelatedSimilarities.length]);
              }
	      else {
		      related.push(this.graph_data[i + this.unrelatedSimilarities.length]);
	      }
      }
      return {
	datasets: [
	  {
      	    data: related,
      	    label:'Related to crisis',
      	    backgroundColor:'#0000ff'
          },
          {
      	    data: unrelated,
      	    label:'Not related',
      	    backgroundColor:'#ff0000'
          }
	]
      };
    }
  }
};
</script>
<style src="@vueform/slider/themes/default.css"></style>

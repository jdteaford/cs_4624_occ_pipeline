<template>
	<div class="main">
		<div class="subpage_box">
		<div class="dot_holder">
				<div class="dot1" @click="$router.push('/')"></div>
				<div class="dot2"></div>
				<div class="dot3"></div>
		</div>
		<div class="title">
		    <h2 id="titletrain">Perform Training</h2>
		</div>
		<form class="main_form">
		<div class="content-left">
		<div class="align-horizontal">
	    	<p class="label">Upload Train Data</p>
	    	<p class="upload_type"><input type="file" ref="trainData" @change="updateTrainData" multiple></p>
		</div>
		<div class="align-horizontal">
	    	<p class="label">Train Model Type</p>
	    	<p class="upload_type">
		<select v-model="train_model_type">
		    	<option></option>
	    	        <option value='svm'>One-class SVM</option>
	    	        <option value='ae'>Autoencoder</option>
		</select>
		</p>
		</div>
		<div class="align-horizontal">
	    	<p class="label">Train Data Type</p>
	    	<p class="upload_type"><select v-model="train_data_type">
	    	        <option></option>
	    	        <option value='urls'>Zipfile of URLs</option>
	    	        <option value='html'>Zipfile of HTML</option>
	    	        <option value='txt'>Zipfile of .txt files</option>
	    	</select></p>
		</div>
		<div class="align-horizontal">
	    <p class="align-center"><button type="button" @click="train">Perform Training</button></p>
		</div>
		</div>
	</form>
	<div v-if="show_loss_curve" class="loss_curve">
    <Line :data="graph_data" :options="graph_options" />
	</div>
</div>
		</div>
</template>
<script>
import axios from 'axios';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js'
import { Line } from 'vue-chartjs'

export default {
  components: {
    Line
  },
  data() {
    return {
      inference_data: [],
      inference_data_type: '',
      inference_model: [],
      inference_model_type: '',
      train_data: [],
      train_model_type: '',
      train_data_type: '',
      show_loss_curve: false,
      trained_model: '',
      graph_data: {
        labels: [],
        datasets: [{
	  data: []
	}]
      },
      graph_options: {
        responsive: true
      }
    };
  },
  methods: {
    train() {
	  const path = 'http://localhost:8000/train';
	  let formData = new FormData();
	  formData.append("data", this.train_data[0]);
	  formData.append("data_type", this.train_data_type);
	  formData.append("model_type", this.train_model_type);
	  this.submitForm(path, formData);
    },
    updateTrainData() {
	  this.train_data = this.$refs.trainData.files;
    },
    submitForm(path, formData) {
	  axios.post(path, formData, {
	    headers: {
	      "Content-Type": "multipart/form-data"
	    },
	  })
      .then((res) => {
	const blob = new Blob([res.data[1]])
        const link = document.createElement('a')
        link.href = URL.createObjectURL(blob)
        link.download = 'model.pickle'
        link.click()
        URL.revokeObjectURL(link.href)

		this.trained_model = res.data[1];
		this.graph_data.datasets = [ { data: res.data[0], label:'Loss Curve', backgroundColor:'#191623' } ];
        this.graph_data.labels = [...Array(res.data[0].length).keys()];
		this.show_loss_curve = true;
		console.log(this.graph_data);
      })
      .catch((error) => {
        console.error(error);
      });
    },
  },
};
</script>

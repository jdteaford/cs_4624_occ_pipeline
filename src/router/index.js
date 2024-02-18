import { createRouter, createWebHistory } from 'vue-router'
import Home from '../components/Home.vue'
import UploadModel from '../components/UploadModel.vue'
import Inference from '../components/Inference.vue'
import Train from '../components/Train.vue'
import Label from '../components/Label.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'Home',
      component: Home 
    },
    {
      path: '/uploadmodel',
      name: 'uploadmodel',
      component: UploadModel
    },
    {
      path: '/inference',
      name: 'inference',
      component: Inference
    },
    {
      path: '/label',
      name: 'label',
      component: Label 
    },
    {
      path: '/train',
      name: 'train',
      component: Train

    }
  ]
})

export default router

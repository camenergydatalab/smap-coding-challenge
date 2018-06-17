import "babel-polyfill"

import Vue from 'vue'
import Vuex from 'vuex'
import { mapState, mapGetters, mapMutations } from 'vuex'

import Base from './Base.vue'

import style from 'c3/c3.min.css'

window.app = new Vue({
  el: "#summary",
  components: {
    Base,
  },
  data: {
  },
  computed: {
  },
  template: '<Base />',
})

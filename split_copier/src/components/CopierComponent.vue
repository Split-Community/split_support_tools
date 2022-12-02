<template>
    <b-container>
      <template v-if="SPLITS.length > 0">
        <b-row class="mt-3" >
          <b-col>
            <b-form>
              <b-form-group id="input-group-1" label="Copy Split:" label-for="input-1">
                <b-form-select id="input-1" v-model="form.selected" :options="splitOptions" @update="resetSplit"></b-form-select>
              </b-form-group>
              <b-form-group id="input-group-2" label="From environment:" label-for="input-2">
                <b-form-select id="input-2" v-model="form.fromEnv" :options="fromEnvOptions" @update="resetFromDef"></b-form-select>
              </b-form-group>
              <b-form-group id="input-group-3" label="To environment:" label-for="input-3">
                <b-form-select id="input-3" v-model="form.toEnv" :options="toEnvOptions" @update="resetToDef"></b-form-select>
              </b-form-group>
            </b-form>
          </b-col>
        </b-row>  
        <b-row class="mt-3" align-h="between">
          <b-col cols="2">
            <b-button-group>
              <b-button @click="loadPreview" :disabled="!previewEnabled">Preview</b-button>
            </b-button-group>
          </b-col>
          <b-col cols="2" style="text-align: right">
            <b-button-group>
              <b-button variant="success" v-if="canUpdate" @click="saveSplit">Save</b-button>
            </b-button-group>
          </b-col>
        </b-row>
        <b-row class="mt-3" v-if="fromSplitDef != null" >
          <vueJsonCompare :oldData="toSplitDef" :newData="fromSplitDef" />
        </b-row>
      </template>
      <b-row v-else>
        <b-col cols="12" style="text-align: center">
          <b>Configure API key and workspace to copy Splits!</b>
        </b-col>
      </b-row>
    </b-container>
</template>

<script>
import { mapGetters } from 'vuex';
import { MAKE_URL } from '@/js/utils';
import vueJsonCompare from 'vue-json-compare';

export default {
  name: 'CopierComponent',
  components: {
    vueJsonCompare
  },
  data() {
      return {
        form: {
            selected: null,
            fromEnv: null,
            toEnv: null
        },
        fromSplitDef: null,
        toSplitDef: null,
        canUpdate: false,
        IGNORE_KEYS: ['lastTrafficReceivedAt', 'environment', 'creationTime', 'lastUpdateTime', 'changeNumber'],
      }
  },
  methods: {
    async getSplitDef(workspaceId, splitName, environmentId) {
      const url = MAKE_URL(`v2/splits/ws/${workspaceId}/${splitName}/environments/${environmentId}`);
      const response = await fetch(url, {
        method: 'GET', 
        headers: {
          Accept: 'application/json',
          Authorization: `Bearer ${this.API_KEY}`
        }
      });
      if (response.ok) {
        const response_json = await response.json();
        this.IGNORE_KEYS.forEach(function(key) {
          delete response_json[key];
        })
        return response_json;
      } else {
        if (response.status === 404) {
          return {};
        }
        const res = await response.text();
        console.error(res);
        return null;
      }
    },
    async getFromSplitDef() {
      const resp = await this.getSplitDef(this.CURRENT_WORKSPACE, this.form.selected, this.form.fromEnv);
      return resp;
    },
    async getToSplitDef() {
      const resp = await this.getSplitDef(this.CURRENT_WORKSPACE, this.form.selected, this.form.toEnv);
      return resp;
    },
    resetSplit() {
      this.fromSplitDef = null;
      this.toSplitDef = null;
      this.canUpdate = false;
    },
    resetFromDef() {
      this.fromSplitDef = null;
      this.canUpdate = false;
    },
    resetToDef() {
      this.toSplitDef = null;
      this.canUpdate = false;
    },
    resetAll() {
      this.form.selected = null;
      this.form.fromEnv = null;
      this.form.toEnv = null;
      this.resetSplit();
    },
    async loadPreview() {
      const fromDef = await this.getFromSplitDef();
      if (fromDef == null || Object.keys(fromDef).length === 0) {
        this.$toast.error('Cannot find Split definition to copy from!');
        return;
      }
      this.fromSplitDef = fromDef;
      
      const toDef = await this.getToSplitDef();
      if (toDef == null) {
        this.$toast.error('Unable to fetch Split definition for to environment');
        return;
      }
      this.toSplitDef = toDef;
      this.canUpdate = true;
    },
    async saveSplit() {
      const url = MAKE_URL(`v2/splits/ws/${this.CURRENT_WORKSPACE}/${this.form.selected}/environments/${this.form.toEnv}`);
      const response = await fetch(url, {
        method: Object.keys(this.toSplitDef).length === 0 ? 'POST' : 'PUT', 
        headers: {
          Accept: 'application/json',
          Authorization: `Bearer ${this.API_KEY}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(this.fromSplitDef),
      });
      if (response.ok) {
        this.$toast.success('Updated Split definition');
        this.resetAll();
      } else {
        const res = await response.text();
        console.error(res);
      }
    },
  },
  computed: {
    splitOptions() {
      return [
        { value: null, text: 'Select split', disabled: true },
        ...this.SPLITS.map((split) => ({ value: split.name, text: split.name }))
      ]
    },
    fromEnvOptions() {
      const toEnv = this.toEnv;
      return [
        { value: null, text: 'Select environment', disabled: true },
        ...this.ENVIRONMENTS.filter(function(env) {
          return env.id !== toEnv;
        }, this).map((env) => ({ value: env.id, text: env.name })),
      ];
    },
    toEnvOptions() {
      const fromEnv = this.fromEnv;
      return [
        { value: null, text: 'Select environment', disabled: true },
        ...this.ENVIRONMENTS.filter(function(env) {
          return env.id !== fromEnv;
        }, this).map((env) => ({ value: env.id, text: env.name })),
      ];
    },
    previewEnabled() {
      return this.form.selected != null && this.form.fromEnv != null && this.form.toEnv != null;
    },
    ...mapGetters(['SPLITS', 'ENVIRONMENTS', 'API_KEY', 'CURRENT_WORKSPACE']),
  }
};
</script>

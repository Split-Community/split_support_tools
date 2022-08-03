<template>
    <div>
        <b-form>
          <b-form-group id="input-group-1" label="Copy Split:" label-for="input-1">
            <b-form-select id="input-1" v-model="form.selected" :options="[]"></b-form-select>
          </b-form-group>
          <b-form-group id="input-group-2" label="From environment:" label-for="input-2">
            <b-form-select id="input-2" v-model="form.fromEnv" :options="[]"></b-form-select>
          </b-form-group>
          <b-form-group id="input-group-3" label="To environment:" label-for="input-3">
            <b-form-select id="input-3" v-model="form.toEnv" :options="[]"></b-form-select>
          </b-form-group>
        </b-form>
    </div>
</template>

<script>
export default {
  name: 'CopierComponent',
  data() {
      return {
        form: {
            selected: null,
            fromEnv: null,
            toEnv: null
        },
      }
  }
};
</script>

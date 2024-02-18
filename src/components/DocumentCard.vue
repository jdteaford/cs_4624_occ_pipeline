<template >
	<div class="document_card">
		<div class="doc_name">{{doc_name}}</div>
		<div class="doc_inner">
			<div class="doc_inner_holder">
				<div class="doc_label">Cosine Similarity</div>
				<div class="cs">{{rounded_cs}}</div>
			</div>
			<div class="doc_inner_holder">
				<div class="doc_label">Ground Truth</div>
				<div class="lab">{{lab}}</div>
			</div>
			<div class="doc_inner_holder">
				<div class="doc_label">Predicted</div>
				<div class="relevant">{{is_relevant}}</div>
			</div>
		</div>
	</div>
</template>
<script>
export default {
  props: ['related', 'threshold', 'lab'],
  computed: {
    rounded_cs: function() {
      return Math.round(this.related[0] * 100);
    },
    is_relevant() {
      if (this.threshold < this.rounded_cs) {
	      return 'Related';
      }
      return 'Unrelated';
    },
    doc_name: function() {
      return this.related[1];
    }
  }
}
</script>

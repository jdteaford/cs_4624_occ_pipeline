<template>
	<div class="main">
		<div class="main_box">
		<div class="dot_holder">
				<div class="dot1"></div>
				<div class="dot2"></div>
				<div class="dot3"></div>
		</div>
		<div>
		    <div class="title"> 
					<div class="titleh1">
							<h1>C</h1>
					</div>
					<div class="titleh2">
							<h2>risis Events One-</h2>
							<h2>lass Text</h2>
							<h2>lassification</h2>
					</div>
			</div>
			<div class="link_holder">
					<div class="main_link_div">
						<button class="main_link_button" @click="$router.push('/train')">Train Model</button>
					</div>
					<div class="main_link_div">
						<button class="main_link_button" @click="$router.push('/label')">Set Threshold</button>
					</div>
					<div class="main_link_div">
						<button class="main_link_button" @click="$router.push('/inference')">Generate Predictions</button>
					</div>
			</div>
		</div>
		</div>
	</div>
</template>

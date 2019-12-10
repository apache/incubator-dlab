/*
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied.  See the License for the
 * specific language governing permissions and limitations
 * under the License.
 */

import { Component, Inject } from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';

@Component({
  selector: 'notification-dialog',
  template: `
  <div id="dialog-box">
    <header class="dialog-header">
      <h4 class="modal-title"><i class="material-icons">priority_high</i>Warning</h4>
      <button type="button" class="close" (click)="dialogRef.close()">&times;</button>
    </header>
    <div mat-dialog-content class="content message">
      <div *ngIf="data.type === 'list'" class="info">
        <div *ngIf="data.template.notebook.length > 0">
          Following notebook server<span *ngIf="data.template.notebook.length>1">s </span>
          <span *ngFor="let item of data.template.notebook">
            <span class="strong">{{ item.exploratory_name }}</span>
            <span *ngIf="data.template.notebook.length > 1">, </span>
          </span> will be stopped and all computational resources will be stopped/terminated
        </div>
        
        <div *ngIf="data.template.cluster.length > 0">
          <p *ngFor="let item of data.template.cluster">
              Computational resource<span *ngIf="data.template.cluster.length > 1">s </span>
              <span class="strong">{{ item.computational_name }}</span> on <span class="strong">{{ item.exploratory_name }}</span>
              will be stopped
          </p>
        </div>
        <span class="strong">by a schedule in 15 minutes.</span>
      </div>
      <div *ngIf="data.type === 'message'"><span [innerHTML]="data.template"></span></div>
      <div *ngIf="data.type === 'confirmation'" class="confirm-dialog">
        <p *ngIf="data.template; else label">
          <span [innerHTML]="data.template"></span>
        </p>
        <ng-template #label>
          <p>
            <span class="ellipsis label-name strong" matTooltip="{{ data.item.name }}" matTooltipPosition="above" [matTooltipDisabled]="data.item.name.length > 35">
            {{ data.item.name }}</span> will be {{ data.action || 'decommissioned' }}.
          </p>
        </ng-template>
          
        <mat-list *ngIf="data.list && data.list.length && data.type === 'confirmation'">
            <mat-list-item class="list-header sans">
                <div class="endpoint">Project</div>
                <div class="status">Resource</div>
            </mat-list-item>
            <div class="scrolling-content">
                <mat-list-item *ngFor="let project of data.list" class="sans node">
                    <div class="endpoint ellipsis">
                        <div *ngFor="let notebook of project.filtredExploratory">{{notebook.name}}</div>
                    </div>
                    <div class="status ellipsis">{{project.project}}</div>                    
                </mat-list-item>
            </div>
          </mat-list>
          
          <mat-list *ngIf="data.item.endpoints?.length">
            <mat-list-item class="list-header sans">
                <div class="endpoint">Edge node in endpoint</div>
                <div class="status">Further status</div>
            </mat-list-item>
            <div class="scrolling-content">
                <mat-list-item *ngFor="let endpoint of data.item.endpoints" class="sans node">
                    <div class="endpoint ellipsis">{{endpoint.name}}</div>
                    <div class="status terminated">Terminated</div>
                </mat-list-item>
            </div>
        </mat-list>          
        <p class="m-top-20"><span class="strong">Do you want to proceed?</span></p>
          
        <div class="text-center m-top-30 m-bott-10">
          <button type="button" class="butt" mat-raised-button (click)="dialogRef.close()">No</button>
          <button type="button" class="butt butt-success" mat-raised-button (click)="dialogRef.close(true)">Yes</button>
        </div>
      </div>
    </div>
  </div>
  `,
  styles: [`
    .content { color: #718ba6; padding: 20px 50px; font-size: 14px; font-weight: 400; margin: 0; }
    .info { color: #35afd5; }
    .info .confirm-dialog { color: #607D8B; }
    header { display: flex; justify-content: space-between; color: #607D8B; }
    header h4 i { vertical-align: bottom; }
    header a i { font-size: 20px; }
    header a:hover i { color: #35afd5; cursor: pointer; }
    .plur { font-style: normal; }
    .label-name { display: inline-block; width: 100% } 
    .scrolling-content{overflow-y: auto; max-height: 200px; }
    .endpoint { width: 70%; text-align: left; color: #577289;}
    .status { width: 30%;text-align: left;}
    .label { font-size: 15px; font-weight: 500; font-family: "Open Sans",sans-serif;}
    .node { font-weight: 300;}
    .label-name { display: inline-block; width: 100%}
    .scrolling-content{overflow-y: auto; max-height: 200px;}
    .endpoint { width: 280px;text-align: left;}    
  `]
})
export class NotificationDialogComponent {
  constructor(
    public dialogRef: MatDialogRef<NotificationDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: any
  ) {
    console.log(data);
  }
}
